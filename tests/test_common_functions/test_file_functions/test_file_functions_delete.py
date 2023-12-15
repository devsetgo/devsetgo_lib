# -*- coding: utf-8 -*-
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from dsg_lib.functions.file_functions import delete_file


class TestDeleteFile(unittest.TestCase):
    def setUp(self):
        self.tmpdir = TemporaryDirectory()
        self.datadir = Path(self.tmpdir.name) / "data"
        self.datadir.mkdir()
        self.csvdir = self.datadir / "csv"
        self.csvdir.mkdir()
        self.jsondir = self.datadir / "json"
        self.jsondir.mkdir()
        self.textdir = self.datadir / "text"
        self.textdir.mkdir()

        # Create some test files
        self.csvfile = self.csvdir / "test.csv"
        self.csvfile.touch()
        self.jsonfile = self.jsondir / "test.json"
        self.jsonfile.touch()
        self.textfile = self.textdir / "test.txt"
        self.textfile.touch()

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_delete_csv_file(self):
        # Test deleting a CSV file
        filename = "test"
        with patch(
            "dsg_lib.functions.file_functions.directory_to_files",
            str(self.datadir),
        ):
            delete_file(filename + ".csv")
        self.assertFalse(self.csvfile.exists())

    def test_delete_json_file(self):
        # Test deleting a JSON file
        filename = "test"
        with patch(
            "dsg_lib.functions.file_functions.directory_to_files",
            str(self.datadir),
        ):
            delete_file(filename + ".json")
        self.assertFalse(self.jsonfile.exists())

    def test_delete_text_file(self):
        # Test deleting a text file
        filename = "test"
        with patch(
            "dsg_lib.functions.file_functions.directory_to_files",
            str(self.datadir),
        ):
            delete_file(filename + ".txt")
        self.assertFalse(self.textfile.exists())

    def test_delete_nonexistent_file(self):
        # Test deleting a nonexistent file
        filename = "nonexistent"
        with patch(
            "dsg_lib.functions.file_functions.directory_to_files",
            str(self.datadir),
        ):
            with self.assertRaises(FileNotFoundError):
                delete_file(filename + ".csv")

    def test_delete_invalid_filename(self):
        # Test deleting a file with an invalid filename
        with patch(
            "dsg_lib.functions.file_functions.directory_to_files",
            str(self.datadir),
        ):
            with self.assertRaises(ValueError):
                delete_file("invalid/filename.csv")

    def test_delete_unsupported_filetype(self):
        # Test deleting a file with an unsupported filetype
        with patch(
            "dsg_lib.functions.file_functions.directory_to_files",
            str(self.datadir),
        ):
            with self.assertRaises(ValueError):
                delete_file("test.jpg")

    def test_delete_nonstring_filename(self):
        # Test deleting a file with a non-string filename
        with patch(
            "dsg_lib.functions.file_functions.directory_to_files",
            str(self.datadir),
        ):
            with self.assertRaises(TypeError):
                delete_file(123)
