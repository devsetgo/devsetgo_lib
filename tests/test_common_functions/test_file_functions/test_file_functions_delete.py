# -*- coding: utf-8 -*-
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from dsg_lib.common_functions.file_functions import delete_file


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
            "dsg_lib.common_functions.file_functions.directory_to_files",
            str(self.datadir),
        ):
            delete_file(filename + ".csv")
        self.assertFalse(self.csvfile.exists())

    def test_delete_json_file(self):
        # Test deleting a JSON file
        filename = "test"
        with patch(
            "dsg_lib.common_functions.file_functions.directory_to_files",
            str(self.datadir),
        ):
            delete_file(filename + ".json")
        self.assertFalse(self.jsonfile.exists())

    def test_delete_text_file(self):
        # Test deleting a text file
        filename = "test"
        with patch(
            "dsg_lib.common_functions.file_functions.directory_to_files",
            str(self.datadir),
        ):
            delete_file(filename + ".txt")
        self.assertFalse(self.textfile.exists())

    def test_delete_nonexistent_file(self):
        # Test deleting a nonexistent file
        filename = "nonexistent"
        with patch(
            "dsg_lib.common_functions.file_functions.directory_to_files",
            str(self.datadir),
        ):
            with self.assertRaises(FileNotFoundError):
                delete_file(filename + ".csv")

    def test_delete_invalid_filename(self):
        # Test deleting a file with an invalid filename
        with patch(
            "dsg_lib.common_functions.file_functions.directory_to_files",
            str(self.datadir),
        ):
            with self.assertRaises(ValueError):
                delete_file("invalid/filename.csv")

    def test_delete_invalid_filename_backslash(self):
        # Backslash must be rejected too, not just forward slash -- the
        # validation now checks both consistently across file_functions.
        with patch(
            "dsg_lib.common_functions.file_functions.directory_to_files",
            str(self.datadir),
        ):
            with self.assertRaises(ValueError):
                delete_file("invalid\\filename.csv")

    def test_delete_unsupported_filetype(self):
        # Test deleting a file with an unsupported filetype
        with patch(
            "dsg_lib.common_functions.file_functions.directory_to_files",
            str(self.datadir),
        ):
            with self.assertRaises(ValueError):
                delete_file("test.jpg")

    def test_delete_nonstring_filename(self):
        # Test deleting a file with a non-string filename
        with patch(
            "dsg_lib.common_functions.file_functions.directory_to_files",
            str(self.datadir),
        ):
            with self.assertRaises(TypeError):
                delete_file(123)

    def test_delete_file_with_explicit_root_folder(self):
        # A file saved directly in a custom root_folder (matching
        # save_json/save_csv/save_text's direct-placement behavior) must be
        # deletable via delete_file(root_folder=...) without needing to patch
        # module-level directory_to_files.
        custom_folder = self.datadir / "custom"
        custom_folder.mkdir()
        custom_file = custom_folder / "custom.csv"
        custom_file.touch()

        delete_file("custom.csv", root_folder=str(custom_folder))
        self.assertFalse(custom_file.exists())

    def test_delete_file_with_root_folder_not_found(self):
        # root_folder must be honored precisely -- it should not fall back
        # to the default data/<type> directory when the file isn't there.
        with self.assertRaises(FileNotFoundError):
            delete_file("test.csv", root_folder=str(self.datadir / "empty"))
