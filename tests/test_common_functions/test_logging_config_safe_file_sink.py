# -*- coding: utf-8 -*-
import os
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import pytest

from dsg_lib.common_functions.logging_config import SafeFileSink


class TestSafeFileSinkParsing:
    def test_parse_size_mb(self):
        assert SafeFileSink.parse_size("100MB") == 100 * 1024 * 1024

    def test_parse_size_gb(self):
        assert SafeFileSink.parse_size("2GB") == 2 * 1024 * 1024 * 1024

    def test_parse_size_kb(self):
        assert SafeFileSink.parse_size("500KB") == 500 * 1024

    def test_parse_size_plain_bytes(self):
        assert SafeFileSink.parse_size("12345") == 12345

    def test_parse_duration_days(self):
        assert SafeFileSink.parse_duration("7 days") == timedelta(days=7)

    def test_parse_duration_hours(self):
        assert SafeFileSink.parse_duration("3 hours") == timedelta(hours=3)

    def test_parse_duration_minutes(self):
        assert SafeFileSink.parse_duration("10 minutes") == timedelta(minutes=10)

    def test_parse_duration_unrecognized_defaults_to_zero(self):
        assert SafeFileSink.parse_duration("forever") == timedelta(days=0)


class TestSafeFileSinkFileOps:
    @pytest.fixture(autouse=True)
    def setup_log_file(self):
        with TemporaryDirectory() as tmp:
            self.tmp = tmp
            self.log_path = Path(tmp) / "app.log"
            self.log_path.touch()
            yield

    def test_write_message_appends(self):
        sink = SafeFileSink(str(self.log_path), rotation="100MB", retention="30 days")
        sink.write_message("hello\n")
        sink.write_message("world\n")
        assert self.log_path.read_text() == "hello\nworld\n"

    def test_rotate_logs_no_rotation_when_under_threshold(self):
        self.log_path.write_text("small")
        sink = SafeFileSink(str(self.log_path), rotation="1MB", retention="30 days")
        assert sink.rotate_logs() is False
        assert self.log_path.exists()

    def test_rotate_logs_rotates_when_over_threshold_no_compression(self):
        self.log_path.write_text("x" * 100)
        sink = SafeFileSink(str(self.log_path), rotation="10", retention="30 days")
        assert sink.rotate_logs() is True
        assert not self.log_path.exists()
        rotated = [p for p in Path(self.tmp).iterdir() if p.name.startswith("app.log.")]
        assert len(rotated) == 1

    def test_rotate_logs_compresses_and_removes_uncompressed(self):
        self.log_path.write_text("x" * 100)
        sink = SafeFileSink(
            str(self.log_path), rotation="10", retention="30 days", compression="zip"
        )
        assert sink.rotate_logs() is True

        remaining = list(Path(self.tmp).iterdir())
        zip_files = [p for p in remaining if p.suffix == ".zip"]
        assert len(zip_files) == 1

        # the uncompressed rotated file must have been cleaned up
        uncompressed = [
            p for p in remaining if p.name.startswith("app.log.") and p.suffix != ".zip"
        ]
        assert uncompressed == []

        # and the archive actually contains the rotated log's content
        with zipfile.ZipFile(zip_files[0]) as z:
            contents = b"".join(z.read(n) for n in z.namelist())
        assert contents == b"x" * 100

    def test_apply_retention_removes_old_rotated_files_keeps_recent(self):
        old_file = Path(self.tmp) / "app.log.old"
        old_file.write_text("old")
        recent_file = Path(self.tmp) / "app.log.recent"
        recent_file.write_text("recent")

        old_time = (datetime.now() - timedelta(days=40)).timestamp()
        os.utime(old_file, (old_time, old_time))

        sink = SafeFileSink(str(self.log_path), rotation="100MB", retention="30 days")
        sink.apply_retention()

        assert not old_file.exists()
        assert recent_file.exists()

    def test_apply_retention_never_deletes_the_active_log_file(self):
        # Regression test: apply_retention's original filter
        # (filename.startswith(basename) and "." in filename) also matched
        # the active log file itself (e.g. "app.log".split(".") has length
        # 2), so a quiet app whose log file goes stale could have its live
        # log file deleted out from under it.
        old_time = (datetime.now() - timedelta(days=400)).timestamp()
        os.utime(self.log_path, (old_time, old_time))

        sink = SafeFileSink(str(self.log_path), rotation="100MB", retention="30 days")
        sink.apply_retention()

        assert self.log_path.exists()


class TestSafeFileSinkRetentionThrottling:
    """
    Covers the performance fix: apply_retention() does a full directory scan
    (os.listdir + os.path.getmtime per matching file), which is too expensive
    to run on every single log message. It must only run right after an
    actual rotation, or at most once per retention_check_interval seconds.
    """

    @pytest.fixture(autouse=True)
    def setup_log_file(self):
        with TemporaryDirectory() as tmp:
            self.tmp = tmp
            self.log_path = Path(tmp) / "app.log"
            self.log_path.touch()
            yield

    def test_apply_retention_not_called_on_every_message_without_rotation(self):
        sink = SafeFileSink(
            str(self.log_path),
            rotation="100MB",  # never rotates during this test
            retention="30 days",
            retention_check_interval=60,
        )
        with patch.object(sink, "apply_retention") as mock_retention, patch(
            "dsg_lib.common_functions.logging_config.time.monotonic", return_value=1000.0
        ):
            for _ in range(50):
                sink("a log line\n")

        # 50 messages, no rotation, all within the same instant -- retention
        # should have swept exactly once (the very first call establishes
        # the baseline), not on every message.
        assert mock_retention.call_count == 1

    def test_apply_retention_called_immediately_after_rotation(self):
        sink = SafeFileSink(
            str(self.log_path),
            rotation="10",  # rotates almost immediately
            retention="30 days",
            retention_check_interval=3600,  # long interval, so only rotation should trigger it
        )
        with patch.object(sink, "apply_retention") as mock_retention, patch(
            "dsg_lib.common_functions.logging_config.time.monotonic", return_value=1000.0
        ):
            sink("a log line\n")  # under threshold, no rotation yet
            assert mock_retention.call_count == 1  # first-ever call still sweeps

            mock_retention.reset_mock()
            sink("x" * 50)  # pushes file over the rotation threshold

        assert mock_retention.call_count == 1

    def test_apply_retention_runs_again_after_interval_elapses(self):
        sink = SafeFileSink(
            str(self.log_path),
            rotation="100MB",
            retention="30 days",
            retention_check_interval=60,
        )
        with patch.object(sink, "apply_retention") as mock_retention:
            with patch(
                "dsg_lib.common_functions.logging_config.time.monotonic",
                return_value=1000.0,
            ):
                sink("first\n")
            assert mock_retention.call_count == 1

            # still within the interval -- must not sweep again
            with patch(
                "dsg_lib.common_functions.logging_config.time.monotonic",
                return_value=1030.0,
            ):
                sink("second\n")
            assert mock_retention.call_count == 1

            # interval has elapsed -- must sweep again
            with patch(
                "dsg_lib.common_functions.logging_config.time.monotonic",
                return_value=1061.0,
            ):
                sink("third\n")
            assert mock_retention.call_count == 2


class TestSafeFileSinkPersistentHandle:
    """
    Covers the persistent-handle rewrite: one open handle per sink, an
    fstat-based size check, inode-based reopen after external rotation, and
    background compression.
    """

    @pytest.fixture(autouse=True)
    def setup_dir(self):
        with TemporaryDirectory() as tmp:
            self.tmp = Path(tmp)
            self.log_path = self.tmp / "app.log"
            yield

    def test_call_alias_still_writes(self):
        sink = SafeFileSink(str(self.log_path), rotation="1MB", retention="30 days")
        sink("via call\n")
        sink.write("via write\n")
        sink.stop()
        assert self.log_path.read_text() == "via call\nvia write\n"

    def test_handle_is_reused_between_writes(self):
        sink = SafeFileSink(str(self.log_path), rotation="1MB", retention="30 days")
        sink.write("one\n")
        first = sink._fh
        sink.write("two\n")
        assert sink._fh is first
        sink.stop()
        assert sink._fh is None

    def test_creates_missing_directory(self):
        nested = self.tmp / "a" / "b" / "app.log"
        sink = SafeFileSink(str(nested), rotation="1MB", retention="30 days")
        sink.write("hello\n")
        sink.stop()
        assert nested.read_text() == "hello\n"

    @pytest.mark.skipif(os.name == "nt", reason="Windows cannot rename a file another handle holds open")
    def test_reopens_when_file_renamed_externally(self):
        sink = SafeFileSink(
            str(self.log_path), rotation="1MB", retention="30 days", reopen_check_interval=0
        )
        sink.write("before\n")
        moved = self.tmp / "app.log.other-process"
        os.rename(self.log_path, moved)
        sink.write("after\n")
        sink.stop()
        assert moved.read_text() == "before\n"
        assert self.log_path.read_text() == "after\n"

    def test_reopen_check_is_throttled(self):
        sink = SafeFileSink(
            str(self.log_path), rotation="1MB", retention="30 days", reopen_check_interval=3600
        )
        sink.write("one\n")
        with patch.object(SafeFileSink, "_stat_ident") as mock_stat:
            for _ in range(20):
                sink.write("x\n")
        mock_stat.assert_not_called()
        sink.stop()

    def test_fstat_size_sees_external_appends(self):
        sink = SafeFileSink(str(self.log_path), rotation="100", retention="30 days")
        sink.write("small\n")
        # Another process appends through its own handle.
        with open(self.log_path, "a") as other:
            other.write("y" * 200)
        sink.write("trigger\n")
        sink.stop()
        rotated = [p for p in self.tmp.iterdir() if p.name.startswith("app.log.")]
        assert len(rotated) == 1

    @pytest.mark.skipif(os.name == "nt", reason="Windows cannot rename a file another handle holds open")
    def test_stale_handle_does_not_rotate_new_file(self):
        # Simulates: another worker rotated the file while this sink's
        # handle still pointed at the old one. This sink must switch to the
        # new file, not rename it over the other worker's rotated file.
        sink = SafeFileSink(
            str(self.log_path), rotation="10", retention="30 days", reopen_check_interval=3600
        )
        sink.write_message("x" * 20)
        os.rename(self.log_path, self.tmp / "app.log.rotated-by-other")
        self.log_path.write_text("new\n")
        assert sink.rotate_logs() is False
        sink.write_message("mine\n")
        sink.stop()
        assert self.log_path.read_text() == "new\nmine\n"
        assert (self.tmp / "app.log.rotated-by-other").read_text() == "x" * 20

    def test_rotations_in_same_second_do_not_overwrite(self):
        sink = SafeFileSink(str(self.log_path), rotation="5", retention="30 days")
        with patch("dsg_lib.common_functions.logging_config.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 1, 1, 0, 0, 0)
            mock_dt.fromtimestamp = datetime.fromtimestamp
            sink.write("first rotation\n")
            sink.write("second rotation\n")
        sink.stop()
        rotated = sorted(p.name for p in self.tmp.iterdir() if p.name != "app.log")
        assert rotated == ["app.log.20260101_000000", "app.log.20260101_000000_1"]

    def test_rotate_when_file_already_gone(self):
        sink = SafeFileSink(str(self.log_path), rotation="5", retention="30 days")
        sink.write_message("x" * 10)
        sink._close()
        self.log_path.unlink()
        with patch.object(SafeFileSink, "_current_size", return_value=10):
            assert sink.rotate_logs() is False

    def test_background_compression_and_stop_joins(self):
        sink = SafeFileSink(
            str(self.log_path),
            rotation="10",
            retention="30 days",
            compression="zip",
            compress_in_background=True,
        )
        sink.write("x" * 50)
        assert len(sink._compression_threads) == 1
        sink.stop()
        assert sink._compression_threads == []
        zips = [p for p in self.tmp.iterdir() if p.suffix == ".zip"]
        assert len(zips) == 1
        with zipfile.ZipFile(zips[0]) as z:
            assert b"".join(z.read(n) for n in z.namelist()) == b"x" * 50
        leftovers = [p for p in self.tmp.iterdir() if p.name.startswith("app.log.") and p.suffix != ".zip"]
        assert leftovers == []

    def test_sink_is_picklable_with_open_handle(self):
        import pickle

        sink = SafeFileSink(str(self.log_path), rotation="1MB", retention="30 days")
        sink.write("before pickle\n")
        clone = pickle.loads(pickle.dumps(sink))
        assert clone._fh is None
        clone.write("from clone\n")
        clone.stop()
        sink.stop()
        assert self.log_path.read_text() == "before pickle\nfrom clone\n"

    def test_retention_skips_files_removed_concurrently(self):
        (self.tmp / "app.log.old").write_text("old")
        sink = SafeFileSink(str(self.log_path), rotation="1MB", retention="30 days")
        with patch(
            "dsg_lib.common_functions.logging_config.os.path.getmtime",
            side_effect=FileNotFoundError,
        ):
            sink.apply_retention()  # must not raise

    @pytest.mark.skipif(not hasattr(os, "fork"), reason="POSIX only")
    def test_fork_resets_compression_state(self):
        sink = SafeFileSink(str(self.log_path), rotation="1MB", retention="30 days")
        sink._compression_lock.acquire()  # as if compressing when the fork happens
        read_fd, write_fd = os.pipe()
        pid = os.fork()
        if pid == 0:  # pragma: no cover - runs in the child
            ok = sink._compression_lock.acquire(timeout=1) and sink._compression_threads == []
            os.write(write_fd, b"1" if ok else b"0")
            os._exit(0)
        os.close(write_fd)
        result = os.read(read_fd, 1)
        os.waitpid(pid, 0)
        sink._compression_lock.release()
        sink.stop()
        assert result == b"1"

    @pytest.mark.skipif(os.name == "nt", reason="Windows cannot rename a file another handle holds open")
    def test_stale_handle_switches_before_writing(self):
        # Two workers share one log file. A rotates it; B's next message must
        # go to the new file, not into A's rotated (possibly archived) copy.
        worker_a = SafeFileSink(str(self.log_path), rotation="50", retention="30 days", reopen_check_interval=3600)
        worker_b = SafeFileSink(str(self.log_path), rotation="50", retention="30 days", reopen_check_interval=3600)
        worker_b.write("B first\n")
        worker_a.write("A" * 60 + "\n")  # A rotates
        worker_b.write("B second\n")
        worker_a.stop()
        worker_b.stop()
        rotated = [p for p in self.tmp.iterdir() if p.name != "app.log"]
        assert len(rotated) == 1
        assert "B second" not in rotated[0].read_text()
        assert self.log_path.read_text() == "B second\n"

    def test_rotated_name_avoids_any_archive_suffix(self):
        sink = SafeFileSink(str(self.log_path), rotation="5", retention="30 days", compression="gztar")
        (self.tmp / "app.log.20260101_000000.tar.gz").write_text("earlier archive")
        with patch("dsg_lib.common_functions.logging_config.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 1, 1, 0, 0, 0)
            assert sink._rotated_path() == f"{self.log_path}.20260101_000000_1"

    def test_path_keeps_caller_type(self):
        sink = SafeFileSink(self.log_path, rotation="1MB", retention="30 days")
        assert isinstance(sink.path, Path)
        sink.write("path object\n")
        sink.stop()
        assert self.log_path.read_text() == "path object\n"

    def test_current_size_is_zero_without_handle_or_file(self):
        sink = SafeFileSink(str(self.log_path), rotation="1MB", retention="30 days")
        assert not self.log_path.exists()
        assert sink._current_size() == 0
        assert sink.rotate_logs() is False

    def test_compression_thread_is_not_daemon(self):
        # Worker exit joins non-daemon threads, so an archive started just
        # before a worker exits is still finished.
        sink = SafeFileSink(
            str(self.log_path), rotation="10", retention="30 days",
            compression="zip", compress_in_background=True,
        )
        sink.write("x" * 50)
        assert sink._compression_threads[0].daemon is False
        sink.stop()

    def test_failed_compression_leaves_raw_file_not_partial_archive(self):
        sink = SafeFileSink(
            str(self.log_path), rotation="10", retention="30 days",
            compression="zip", compress_in_background=True,
        )
        with patch(
            "dsg_lib.common_functions.logging_config.shutil.make_archive",
            side_effect=OSError("disk full"),
        ):
            sink.write("x" * 50)
            sink.stop()
        names = sorted(p.name for p in self.tmp.iterdir() if p.name != "app.log")
        assert len(names) == 1 and not names[0].endswith(".zip")
        assert (self.tmp / names[0]).read_text() == "x" * 50
