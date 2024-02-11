# -*- coding: utf-8 -*-
import datetime
import os
import time
import unittest
from pathlib import Path

from dsg_lib.common_functions.folder_functions import last_data_files_changed

time_str = datetime.datetime.now(datetime.timezone.utc)


class TestLastDataFilesChanged(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path("test_folder_file_change")
        self.test_dir.mkdir()
        self.file1 = self.test_dir / "file1.txt"
        self.file2 = self.test_dir / "file2.txt"

        # Set the modification time of file1 to be 1 hour ago
        file1_time_tuple = time.localtime(time.time() - 3600)
        self.file2.touch()
        self.file1.touch()
        # adding sleep time to make sure there is no conflict on last modified file
        time.sleep(0.01)
        self.file1.write_text("test")
        os.utime(
            self.file1,
            times=(time.mktime(file1_time_tuple), self.file1.stat().st_mtime),
        )
        print(f"file1 modification time: {self.file1.stat().st_mtime}")

        # Set the modification time of file2 to be 1 day ago
        file2_time_tuple = time.localtime(time.time() - 86400)
        os.utime(
            self.file2,
            times=(time.mktime(file2_time_tuple), self.file2.stat().st_mtime),
        )
        print(f"file2 modification time: {self.file2.stat().st_mtime}")

    def tearDown(self):
        for path in self.test_dir.glob("**/*"):
            try:
                path.unlink(missing_ok=True)
            except OSError:
                try:
                    path.rmdir()
                except OSError:
                    pass
        self.test_dir.rmdir()

    def test_get_last_modified_file(self):
        # Get the last modified file in the test directory and check that it is file1.txt
        last_modified_time, last_modified_file = last_data_files_changed(self.test_dir)
        print(f"last_modified_time: {last_modified_time}")
        print(f"last_modified_file: {last_modified_file}")
        self.assertEqual(
            last_modified_time,
            datetime.datetime.fromtimestamp(self.file1.stat().st_mtime),
        )
        self.assertEqual(last_modified_file, self.file1)

    def test_empty_directory(self):
        # Get the last modified file in an empty directory and check that None is returned
        empty_dir = Path("empty_dir")
        empty_dir.mkdir()
        last_modified_time, last_modified_file = last_data_files_changed(empty_dir)
        self.assertIsNone(last_modified_time)
        self.assertIsNone(last_modified_file)
        empty_dir.rmdir()

    def test_nonexistent_directory(self):
        # Get the last modified file in a nonexistent directory and check that None is returned
        nonexistent_dir = Path("nonexistent_dir")
        last_modified_time, last_modified_file = last_data_files_changed(
            nonexistent_dir
        )
        self.assertIsNone(last_modified_time)
        self.assertIsNone(last_modified_file)
