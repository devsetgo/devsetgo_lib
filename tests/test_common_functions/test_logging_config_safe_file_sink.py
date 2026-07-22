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
