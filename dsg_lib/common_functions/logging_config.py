# -*- coding: utf-8 -*-
"""
This module provides a comprehensive logging setup using the loguru library, facilitating easy logging management for Python applications.

The `config_log` function, central to this module, allows for extensive customization of logging behavior. It supports specifying the logging directory, log file name, logging level, and controls for log rotation, retention, and formatting among other features. Additionally, it offers advanced options like backtrace and diagnose for in-depth debugging, the ability to append the application name to the log file for clearer identification, and control over logger propagation via the `log_propagate` parameter.

Usage example:

    from dsg_lib.common_functions.logging_config import config_log

    config_log(
        logging_directory='logs',  # Directory for storing logs
        log_name='log',  # Base name for log files
        logging_level='DEBUG',  # Minimum logging level
        log_rotation='100 MB',  # Size threshold for log rotation
        log_retention='30 days',  # Duration to retain old log files
        log_propagate=False,  # Control log propagation
    )

    # Example log messages
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.error("This is an error message")
    logger.warning("This is a warning message")
    logger.critical("This is a critical message")

Attributes:
    None

Performance notes:
    Logging runs on the host application's request path, so the defaults are
    chosen for low per-message cost:

    * The file sink keeps one open handle and checks the file size with
      `os.fstat` on that handle, instead of opening, closing and stat-ing the
      file for every message.
    * Rotated files are compressed on a background thread, so a rotation
      never blocks the thread that logged.
    * `enqueue` defaults to `False`. loguru's queue pickles every message
      through a multiprocessing pipe, which costs several times more than the
      write itself. Opt in with `enqueue=True` if you need the write fully
      off the calling thread.
    * With `intercept_standard_logging=True`, the stdlib root logger is set to
      `intercept_level` (defaults to `logging_level`), so stdlib records below
      that level are rejected before a `LogRecord` is even built.
    * `log_to_file=False, log_to_stdout=True` skips the file sink entirely,
      which suits containers that ship stdout.

Author:
    Mike Ryan

Date Created:
    2021/07/16

Date Updated:
    2026/10/24

License:
    MIT
"""
import glob
import logging
import os
import shutil
import sys
import threading
import time
import weakref
from datetime import datetime, timedelta
from multiprocessing import Lock
from pathlib import Path
from uuid import uuid4

from loguru import logger

# Shared by every process forked after import, so concurrent workers never
# rename the active log file at the same time. Do not swap this for a
# threading.Lock: that would only serialise threads inside one process.
rotation_lock = Lock()

VALID_LOG_LEVELS = ["DEBUG", "INFO", "ERROR", "WARNING", "CRITICAL"]

# The coloured default is used for stdout. The file sink gets the same layout
# without colour tags: loguru would strip them for a file anyway, and skipping
# the markup parsing makes each message slightly cheaper to format.
DEFAULT_LOG_FORMAT = "<green>{time:YYYY-MM-DD HH:mm:ss.SSSSSS}</green> | <level>{level: <8}</level> | <cyan> {name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
DEFAULT_FILE_LOG_FORMAT = "{time:YYYY-MM-DD HH:mm:ss.SSSSSS} | {level: <8} |  {name}:{function}:{line} - {message}"


class SafeFileSink:
    """
    A loguru file sink with size-based rotation, age-based retention and
    optional compression, safe for several processes writing one file.

    Attributes:
        path (str): The path to the log file.
        rotation_size (int): The size threshold for log rotation in bytes.
        retention_days (timedelta): The duration to retain old log files.
        compression (str, optional): The `shutil.make_archive` format used for
            rotated files (e.g. "zip"), or None to leave them uncompressed.
        retention_check_interval (float): Minimum seconds between retention
            sweeps (see note below).
        reopen_check_interval (float): Minimum seconds between checks that the
            open handle still points at `path` (see note below).
        compress_in_background (bool): Compress rotated files on a background
            thread instead of on the thread that logged.

    Methods:
        parse_size(size_str): Parses a size string (e.g., '100MB') and returns the size in bytes.
        parse_duration(duration_str): Parses a duration string (e.g., '7 days') and returns a timedelta object.
        write(message): Write one formatted message (loguru calls this).
        stop(): Wait for background compression and close the file.

    Note on the hot path:
        Each message costs one buffered write, one flush and one `os.fstat` on
        the already-open descriptor. `fstat` on the descriptor also sees bytes
        appended by other processes sharing the file, which an in-memory byte
        counter would miss.

    Note on multiple processes:
        Forked workers append to the same file; `O_APPEND` keeps their lines
        from interleaving. When one worker rotates, the others still hold a
        handle to the renamed file. At most once per `reopen_check_interval`
        seconds each sink compares the inode at `path` with its open handle
        and reopens if they differ (the same approach as the stdlib
        `WatchedFileHandler`). Before rotating, a sink also confirms its
        handle is still the file at `path`, so a stale handle can never make
        it rename the new file another worker just created. On Windows a file
        another process holds open cannot be renamed, so multi-process
        rotation is only supported on POSIX.

    Note on retention checks:
        Applying the retention policy requires listing the log directory and
        stat-ing every rotated file in it, which is too expensive to do on
        every single log message at real logging volume. Retention is
        instead swept immediately after a rotation actually occurs (a new
        rotated file just appeared, so it's a natural time to prune old
        ones) and otherwise at most once per `retention_check_interval`
        seconds, as a safety net for files that age out between rotations.

    Example:
        safe_file_sink = SafeFileSink(
            path='logs/app.log',
            rotation='100 MB',
            retention='30 days',
            compression='zip'
        )

        # This will set up a log file at 'logs/app.log' with rotation at 100 MB,
        # retention for 30 days, and compression using zip.
    """

    def __init__(
        self,
        path,
        rotation,
        retention,
        compression=None,
        retention_check_interval=60,
        *,
        reopen_check_interval=1.0,
        compress_in_background=False,
    ):
        self.path = path
        self.rotation_size = self.parse_size(rotation)
        self.retention_days = self.parse_duration(retention)
        self.compression = compression
        self.retention_check_interval = retention_check_interval
        self.reopen_check_interval = reopen_check_interval
        self.compress_in_background = compress_in_background
        self._last_retention_check = 0.0
        self._last_reopen_check = 0.0
        self._fh = None
        self._fh_ident = None
        self._compression_lock = threading.Lock()
        self._compression_threads = []
        self._register_fork_reset()

    def _register_fork_reset(self):
        # A worker forked while this process was compressing would inherit a
        # held compression lock and a dead thread, and stop() would then hang.
        # Reset both in the child. A weak reference keeps the registration
        # from holding the sink alive after logger.remove().
        if not hasattr(os, "register_at_fork"):  # pragma: no cover - Windows
            return
        ref = weakref.ref(self)

        def _after_fork_in_child():
            sink = ref()
            if sink is not None:
                sink._reset_after_fork()

        os.register_at_fork(after_in_child=_after_fork_in_child)

    def _reset_after_fork(self):
        self._compression_lock = threading.Lock()
        self._compression_threads = []

    @staticmethod
    def parse_size(size_str):
        """
        Parses a size string and returns the size in bytes.

        Args:
            size_str (str): The size string (e.g., '100MB').

        Returns:
            int: The size in bytes.
        """
        size_str = size_str.upper().replace(" ", "")
        if size_str.endswith("MB"):
            return int(size_str[:-2]) * 1024 * 1024
        elif size_str.endswith("GB"):
            return int(size_str[:-2]) * 1024 * 1024 * 1024
        elif size_str.endswith("KB"):
            return int(size_str[:-2]) * 1024
        else:
            return int(size_str)

    @staticmethod
    def parse_duration(duration_str):
        """
        Parses a duration string and returns a timedelta object.

        Args:
            duration_str (str): The duration string (e.g., '7 days').

        Returns:
            timedelta: The duration as a timedelta object.
        """
        duration_str = duration_str.lower()
        if "day" in duration_str:
            return timedelta(days=int(duration_str.split()[0]))
        elif "hour" in duration_str:
            return timedelta(hours=int(duration_str.split()[0]))
        elif "minute" in duration_str:
            return timedelta(minutes=int(duration_str.split()[0]))
        else:
            return timedelta(days=0)

    def __getstate__(self):
        # Open files, thread locks and threads cannot be pickled. loguru
        # pickles sinks when a handler is sent to a spawned process; the
        # child simply opens its own handle on first write.
        state = self.__dict__.copy()
        state["_fh"] = None
        state["_fh_ident"] = None
        state["_compression_lock"] = None
        state["_compression_threads"] = []
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self._compression_lock = threading.Lock()
        self._register_fork_reset()

    def write(self, message):
        """
        Handles the logging of a message, including writing, rotating, and applying retention policies.

        loguru treats any object with a `write` method as a stream sink and
        calls this once per formatted message.

        Args:
            message (str): The log message to be written.

        This method ensures process-safe logging by acquiring a lock before writing the message
        and rotating the logs if necessary. The retention policy is swept immediately after a
        rotation, and otherwise at most once per `retention_check_interval` seconds -- see the
        class docstring for why it isn't run on every message.
        """
        with rotation_lock:
            # Check before writing as well as after. If another worker rotated
            # the file, our handle still points at the rotated copy, which is
            # always at or over the rotation size. Catching that here switches
            # us to the new file before the message is written; otherwise it
            # would land in a file that compression may already have archived.
            rotated = False
            if self._fh is not None and self._current_size() >= self.rotation_size:
                rotated = self.rotate_logs()
            self.write_message(message)
            rotated = self.rotate_logs() or rotated
            self._maybe_apply_retention(force=rotated)

    # Kept so code that calls the sink directly, as older versions required,
    # still works.
    __call__ = write

    def stop(self):
        """
        Wait for any background compression to finish and close the file.

        loguru calls this from `logger.remove()`.
        """
        for thread in self._compression_threads:
            thread.join()
        self._compression_threads.clear()
        self._close()

    def _maybe_apply_retention(self, force=False):
        """
        Runs apply_retention() if forced (a rotation just happened) or if at
        least retention_check_interval seconds have passed since the last
        sweep. Must be called while holding rotation_lock.
        """
        now = time.monotonic()
        if force or (now - self._last_retention_check) >= self.retention_check_interval:
            self.apply_retention()
            self._last_retention_check = now

    @staticmethod
    def _stat_ident(path):
        try:
            st = os.stat(path)
        except FileNotFoundError:
            return None
        return (st.st_dev, st.st_ino)

    def _close(self):
        if self._fh is not None:
            try:
                self._fh.close()
            finally:
                self._fh = None
                self._fh_ident = None

    def _open(self):
        self._close()
        directory = os.path.dirname(self.path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        self._fh = open(self.path, "a", encoding="utf-8")
        st = os.fstat(self._fh.fileno())
        self._fh_ident = (st.st_dev, st.st_ino)
        self._last_reopen_check = time.monotonic()

    def _ensure_open(self):
        """
        Make sure the handle is open and still points at `self.path`.

        The path is only re-checked once per `reopen_check_interval`
        seconds, so the common case costs one clock read.
        """
        if self._fh is None:
            self._open()
            return
        now = time.monotonic()
        if now - self._last_reopen_check < self.reopen_check_interval:
            return
        self._last_reopen_check = now
        if self._stat_ident(self.path) != self._fh_ident:
            # Another process rotated (or someone deleted) the file.
            self._open()

    def write_message(self, message):
        """
        Writes a log message to the log file.

        Args:
            message (str): The log message to be written.

        The message is written to a persistent handle and flushed at once, so
        other processes and the size check see it immediately.
        """
        self._ensure_open()
        self._fh.write(message)
        self._fh.flush()

    def _current_size(self):
        if self._fh is not None:
            return os.fstat(self._fh.fileno()).st_size
        try:
            return os.path.getsize(self.path)
        except FileNotFoundError:
            return 0

    def _rotated_path(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        candidate = f"{self.path}.{timestamp}"
        counter = 1
        # Two rotations in the same second must not overwrite each other.
        # glob covers every archive suffix (.zip, .tar.gz, ...), not just
        # ".<compression>", which make_archive does not always use.
        while os.path.exists(candidate) or glob.glob(glob.escape(candidate) + ".*"):
            candidate = f"{self.path}.{timestamp}_{counter}"
            counter += 1
        return candidate

    def rotate_logs(self) -> bool:
        """
        Rotates the log file if it exceeds the specified rotation size.

        This method checks the size of the current log file. If the file size exceeds the
        specified rotation size, it renames the current log file by appending a timestamp to
        its name. Optionally, it compresses the rotated log file using the specified
        compression method and removes the original uncompressed file. The next write opens
        a fresh file at `path`.

        Args:
            None

        Returns:
            bool: True if the log file was rotated, False otherwise.

        Raises:
            OSError: If there is an error renaming or compressing the log file.
        """
        if self._current_size() < self.rotation_size:
            return False

        if self._fh is not None and self._stat_ident(self.path) != self._fh_ident:
            # Our handle points at a file another process already rotated.
            # Switch to the new file instead of renaming it.
            self._open()
            return False

        self._close()
        # The file can vanish between the size check and here (another process
        # rotated or deleted it); the next write opens a fresh one.
        if not os.path.exists(self.path):
            return False
        rotated_path = self._rotated_path()
        os.rename(self.path, rotated_path)
        if self.compression:
            if self.compress_in_background:
                self._compression_threads = [
                    t for t in self._compression_threads if t.is_alive()
                ]
                thread = threading.Thread(
                    target=self._compress,
                    args=(rotated_path,),
                    name="dsg_lib-log-compress",
                    # Not a daemon: interpreter and multiprocessing-worker exit
                    # wait for non-daemon threads, so a worker that exits right
                    # after rotating still finishes its archive.
                    daemon=False,
                )
                self._compression_threads.append(thread)
                thread.start()
            else:
                self._compress(rotated_path)
        return True

    def _compress(self, rotated_path):
        """
        Archive one rotated file and remove the uncompressed copy.

        Errors are written to stderr rather than logged: logging from inside
        the sink could recurse into this sink.
        """
        with self._compression_lock:
            try:
                # Build under a temporary name and rename into place, so a
                # process killed mid-compression leaves the raw rotated file
                # plus a ".compressing" leftover (pruned by retention), never a
                # truncated archive under the final name.
                temp_base = f"{rotated_path}.compressing"
                archive = shutil.make_archive(
                    temp_base,
                    self.compression,
                    root_dir=os.path.dirname(rotated_path),
                    base_dir=os.path.basename(rotated_path),
                )
                os.replace(archive, f"{rotated_path}{archive[len(temp_base):]}")
                os.remove(rotated_path)
            except Exception as ex:  # pragma: no cover - depends on disk errors
                if not self.compress_in_background:
                    raise
                print(
                    f"dsg_lib SafeFileSink: compressing {rotated_path} failed: {ex}",
                    file=sys.stderr,
                )

    def apply_retention(self):
        """
        Applies the retention policy to remove old log files.

        This method iterates through the rotated log files in the directory of the current log
        file (never the active log file itself). It checks the modification time of each and
        removes those older than the specified retention period.

        Args:
            None

        Returns:
            None

        Raises:
            OSError: If there is an error removing a log file.
        """
        now = datetime.now()
        base_name = os.path.basename(self.path)
        # dirname() of a bare filename is "", which os.listdir() rejects.
        directory = os.path.dirname(self.path) or "."
        for filename in os.listdir(directory):
            # Never consider the active log file itself for removal -- only
            # rotated variants (e.g. "app.log.20260101") are eligible.
            if filename == base_name:
                continue
            if filename.startswith(base_name) and len(filename.split(".")) > 1:
                file_path = os.path.join(directory, filename)
                try:
                    file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    if now - file_time > self.retention_days:
                        os.remove(file_path)
                except FileNotFoundError:
                    # Another process removed or compressed it first.
                    continue


# stdlib level name -> loguru level name, filled on first use of each name.
_LEVEL_NAME_CACHE = {}


class InterceptHandler(logging.Handler):
    """
    A logging handler that intercepts standard logging messages and redirects them to Loguru.

    This handler captures log messages from the standard logging module and forwards them to Loguru, preserving the log level and message details.

    Methods:
        emit(record):
            Emits a log record to Loguru.
    """

    def emit(self, record):
        """
        Emits a log record to Loguru.

        This method captures the log record, determines the appropriate Loguru log level, and logs the message using Loguru. It also handles exceptions and finds the caller's frame to maintain accurate log information.

        Args:
            record (logging.LogRecord): The log record to be emitted.

        Returns:
            None
        """
        # Get corresponding Loguru level if it exists
        level = _LEVEL_NAME_CACHE.get(record.levelname)
        if level is None:
            try:
                level = logger.level(record.levelname).name
                _LEVEL_NAME_CACHE[record.levelname] = level
            except ValueError:  # pragma: no cover
                level = record.levelno  # pragma: no cover

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:  # pragma: no cover
            frame = frame.f_back  # pragma: no cover
            depth += 1  # pragma: no cover

        # Log the message using loguru
        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )  # pragma: no cover


def _validate_level(name, value):
    if value.upper() not in VALID_LOG_LEVELS:
        raise ValueError(
            f"Invalid {name}: {value}. Valid levels are: {VALID_LOG_LEVELS}"
        )
    return value.upper()


def config_log(
    logging_directory: str = "log",
    log_name: str = "log",
    logging_level: str = "INFO",
    log_rotation: str = "100 MB",
    log_retention: str = "30 days",
    log_backtrace: bool = False,
    log_format: str = None,
    log_serializer: bool = False,
    log_diagnose: bool = False,
    app_name: str = None,
    append_app_name: bool = False,
    enqueue: bool = False,
    intercept_standard_logging: bool = True,
    log_propagate: bool = False,
    compression: str = "zip",
    log_retention_check_interval: float = 60,
    intercept_level: str = None,
    log_to_file: bool = True,
    log_to_stdout: bool = False,
    log_compress_in_background: bool = True,
):
    """
    Configures the logging settings for the application.

    This function sets up the logging configuration, including the log directory, log file name, logging level, log rotation, retention policies, and other optional settings.

    Args:
        logging_directory (str): The directory where log files will be stored. Defaults to "log".
        log_name (str): The base name of the log file. Defaults to "log".
        logging_level (str): The logging level (e.g., "INFO", "DEBUG"). Defaults to "INFO".
        log_rotation (str): The size threshold for log rotation (e.g., "100 MB"). Defaults to "100 MB".
        log_retention (str): The duration to retain old log files (e.g., "30 days"). Defaults to "30 days".
        log_backtrace (bool): Whether to include backtrace information in logs. Defaults to False.
        log_format (str, optional): The format string for log messages. Defaults to a predefined format if not provided.
        log_serializer (bool): Whether to serialize log messages. Defaults to False.
        log_diagnose (bool): Whether to include diagnostic information in logs. Defaults to False.
        app_name (str, optional): The name of the application. Defaults to None.
        append_app_name (bool): Whether to append the application name to the log file name. Defaults to False.
        enqueue (bool): Whether to route messages through loguru's multiprocessing queue. Defaults to False. The queue pickles every message and sends it through a pipe, which costs several times more per call than the file write itself (about 85 µs vs 11 µs per message in this repo's `speedtest/logging_bench.py`). Set it to True only if writes must happen entirely off the calling thread, or if you start worker processes with the `spawn` method and need loguru to funnel their messages to one writer.
        intercept_standard_logging (bool): Whether to intercept standard logging calls. Defaults to True.
        log_propagate (bool): Whether to propagate log messages to ancestor loggers. Defaults to False.
        compression (str): The compression method for rotated log files (e.g., "zip"). Defaults to 'zip'.
        log_retention_check_interval (float): Minimum seconds between retention sweeps outside of a rotation event. Retention is always swept immediately after a rotation; this just bounds how often the (directory-scanning) sweep otherwise runs. Defaults to 60.
        intercept_level (str, optional): Lowest stdlib `logging` level forwarded to loguru when `intercept_standard_logging` is True. Defaults to `logging_level`. The stdlib root logger is set to this level, so lower records (for example SQLAlchemy or httpx DEBUG output) are rejected before a record is built, instead of being formatted and then discarded by loguru. Set it lower than `logging_level` only if you add another loguru sink at a lower level that needs stdlib records.
        log_to_file (bool): Whether to write to the rotating log file. Defaults to True.
        log_to_stdout (bool): Whether to also write to stdout. Defaults to False. For containers that ship stdout, use `log_to_file=False, log_to_stdout=True` to skip file I/O entirely.
        log_compress_in_background (bool): Whether rotated files are compressed on a background thread. Defaults to True, so a rotation never blocks the thread that logged while a large file is zipped.

    Raises:
        ValueError: If `logging_level` or `intercept_level` is not a valid level, or if both `log_to_file` and `log_to_stdout` are False.

    Returns:
        None

    Example:
        config_log(
            logging_directory='logs',
            log_name='app_log',
            logging_level='DEBUG',
            log_rotation='50 MB',
            log_retention='7 days',
            log_backtrace=True,
            log_format='{time} - {level} - {message}',
            log_serializer=True,
            log_diagnose=True,
            app_name='MyApp',
            append_app_name=True,
            intercept_standard_logging=False,
            log_propagate=False,
            compression='gz'
        )

    This will configure the logging settings with the specified parameters, setting up a log file at 'logs/app_log' with rotation at 50 MB, retention for 7 days, and other specified options.

    Container example (JSON lines to stdout, no file):
        config_log(log_to_file=False, log_to_stdout=True, log_serializer=True)
    """

    if not log_to_file and not log_to_stdout:
        raise ValueError("at least one of log_to_file or log_to_stdout must be True")

    # If the log_name ends with ".log", remove the extension
    if log_name.endswith(".log"):
        log_name = log_name.replace(".log", "")  # pragma: no cover

    # If the log_name ends with ".json", remove the extension
    if log_name.endswith(".json"):
        log_name = log_name.replace(".json", "")  # pragma: no cover

    # Set default log format if not provided
    file_log_format = log_format
    if log_format is None:  # pragma: no cover
        log_format = DEFAULT_LOG_FORMAT  # pragma: no cover
        file_log_format = DEFAULT_FILE_LOG_FORMAT  # pragma: no cover

    if log_serializer is True:
        log_format = file_log_format = "{message}"  # pragma: no cover
        log_name = f"{log_name}.json"  # pragma: no cover
    else:
        log_name = f"{log_name}.log"  # pragma: no cover

    # Validate logging levels
    level = _validate_level("logging level", logging_level)
    stdlib_level = _validate_level("intercept level", intercept_level or logging_level)

    # Generate unique trace ID
    trace_id: str = str(uuid4())
    logger.configure(extra={"app_name": app_name, "trace_id": trace_id})

    # Append app name to log format if provided
    if app_name is not None:
        log_format += " | app_name: {extra[app_name]}"
        file_log_format += " | app_name: {extra[app_name]}"

    # Remove any previously added sinks
    logger.remove()

    sink_options = {
        "level": level,
        "format": log_format,
        "enqueue": enqueue,
        "backtrace": log_backtrace,
        "serialize": log_serializer,
        "diagnose": log_diagnose,
    }

    if log_to_file:
        # Append app name to log file name if required
        if append_app_name is True and app_name is not None:
            log_name = log_name.replace(".", f"_{app_name}.")

        # Construct log file path
        log_path = Path.cwd().joinpath(logging_directory).joinpath(log_name)

        logger.add(
            SafeFileSink(
                log_path,
                rotation=log_rotation,
                retention=log_retention,
                compression=compression,
                retention_check_interval=log_retention_check_interval,
                compress_in_background=log_compress_in_background,
            ),
            **{**sink_options, "format": file_log_format},
        )

    if log_to_stdout:
        logger.add(sys.stdout, **sink_options)

    if intercept_standard_logging:
        # One shared handler instance; levels below stdlib_level never reach it.
        handler = InterceptHandler(level=stdlib_level)

        # Remove all handlers from all loggers to prevent duplicates
        for logger_name in logging.Logger.manager.loggerDict:
            log_instance = logging.getLogger(logger_name)
            log_instance.handlers = []
            # Optionally, set propagate to False if you want to avoid double propagation
            log_instance.propagate = log_propagate

        # Remove handlers from root logger
        root_logger = logging.getLogger()
        root_logger.handlers = []

        # Add InterceptHandler to all loggers (including root)
        for logger_name in logging.Logger.manager.loggerDict:
            logging.getLogger(logger_name).addHandler(handler)
        root_logger.addHandler(handler)

        # Loggers left at NOTSET inherit this level, so stdlib calls below it
        # return immediately instead of building a record loguru would drop.
        root_logger.setLevel(stdlib_level)
    else:
        # If not intercepting, you may want to configure basicConfig as before
        logging.basicConfig(level=level)  # pragma: no cover
