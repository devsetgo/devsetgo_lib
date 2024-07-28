"""
This module provides a logging configuration setup with structlog, including
support for safe log rotation and multiprocessing.
"""

import logging
import logging.handlers
import os
import threading
from collections import deque
from datetime import datetime
from multiprocessing import Lock, Process, Queue
from queue import Empty

import structlog
from pythonjsonlogger import jsonlogger

rotation_lock = Lock()

class SafeRotatingFileHandler(logging.handlers.RotatingFileHandler):
    """A rotating file handler that safely handles log file rotation."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.process_name = os.getpid()  # Get the process ID

    def doRollover(self):
        """Perform the log file rollover."""
        with rotation_lock:
            if self.stream:
                self.stream.close()
                self.stream = None

            dfn = self.rotation_filename(f"{self.baseFilename}.{self.process_name}.{self.backupCount}")
            if os.path.exists(dfn):
                os.remove(dfn)
            self.rotate(self.baseFilename, dfn)

            if not self.delay:
                self.stream = self._open()

class QueueHandler(logging.Handler):
    """This is a logging handler which sends events to a queue. It can be used
    from different processes to send logs to a single log file.
    """
    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record):
        try:
            self.log_queue.put_nowait(record)
        except Exception as e:
            print(f"Error emitting log record: {e}")

class QueueListener:
    """This is a listener which receives log events from the queue and processes
    them. It should be run in a separate process.
    """
    def __init__(self, log_queue, handlers):
        self.log_queue = log_queue
        self.handlers = handlers
        self.stop_event = threading.Event()

    def start(self):
        """Start the queue listener."""
        while not self.stop_event.is_set():
            try:
                record = self.log_queue.get(timeout=0.05)
                self.handle(record)
            except Empty:
                continue

    def handle(self, record):
        """Handle a log record."""
        for handler in self.handlers:
            handler.handle(record)

    def stop(self):
        """Stop the queue listener."""
        self.stop_event.set()

class CachingRotatingFileHandler(logging.handlers.RotatingFileHandler):
    """A rotating file handler with caching capabilities."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cache = deque(maxlen=1000)

    def emit(self, record):
        """Emit a record."""
        try:
            self.cache.append(record)
        except Exception as e:
            print(f"Error caching log record: {e}")

    def flush_cache(self):
        """Flush the cache."""
        while self.cache:
            record = self.cache.popleft()
            super().emit(record)

def configure_logging(
    logging_directory: str = 'log',
    log_name: str = 'log',
    logging_level: str = 'INFO',
    log_rotation: int = 100,  # Size in MB
    log_retention: int = 10,
    multiprocess: bool = False
):
    """Configure logging with rotating file handlers."""
    if not os.path.exists(logging_directory):
        os.makedirs(logging_directory)

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    log_name = f"{log_name}_{timestamp}.json"
    log_path = os.path.join(logging_directory, log_name)
    max_bytes = log_rotation * 1024 * 1024

    cache_rotating_handler = CachingRotatingFileHandler(
        log_path,
        maxBytes=max_bytes,
        backupCount=log_retention
    )
    safe_rotating_file_handler = SafeRotatingFileHandler(
        filename=log_path,
        maxBytes=max_bytes,
        backupCount=log_retention
    )
    formatter = jsonlogger.JsonFormatter()
    cache_rotating_handler.setFormatter(formatter)
    safe_rotating_file_handler.setFormatter(formatter)

    handlers = [cache_rotating_handler, safe_rotating_file_handler]

    listener_process, listener_instance = None, None

    if multiprocess:
        log_queue = Queue()
        queue_handler = QueueHandler(log_queue)
        handlers = [queue_handler]
        listener_instance = QueueListener(log_queue, [cache_rotating_handler, safe_rotating_file_handler])
        listener_process = Process(target=listener_instance.start)
        listener_process.start()

    logging.basicConfig(
        level=logging_level,
        handlers=handlers
    )

    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    cache_rotating_handler.flush_cache()

    return listener_instance, listener_process

# Example usage
if __name__ == "__main__":
    listener_instance, listener_process = configure_logging(
        logging_directory='log',
        log_name='log',
        logging_level='INFO',
        log_rotation=100,  # Size in MB
        log_retention=10,
        multiprocess=True
    )

    logger = structlog.get_logger()
    logger.info("Logging configured with SafeRotatingFileHandler")
