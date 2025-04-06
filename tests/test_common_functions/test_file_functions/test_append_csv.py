import unittest
from pathlib import Path
from unittest.mock import patch
from dsg_lib.common_functions.file_functions import append_csv, save_csv


class TestAppendCSV(unittest.TestCase):
    def setUp(self):
        self.test_data = [
            ["Name", "Email"],
            ["John Doe", "jdoe@example.com"],
        ]
        self.append_data = [
            ["Name", "Email"],
            ["Jane Smith", "jsmith@example.com"],
        ]
        self.csv_path = Path("data/csv/test_append.csv")
        if self.csv_path.exists():
            self.csv_path.unlink()

    def tearDown(self):
        if self.csv_path.exists():
            self.csv_path.unlink()

    @patch("dsg_lib.common_functions.file_functions.directory_to_files", "data")
    def test_append_csv_valid_data(self):
        save_csv("test_append", self.test_data)
        result = append_csv("test_append", self.append_data)
        self.assertEqual(result, "appended")
        self.assertTrue(self.csv_path.exists())

    @patch("dsg_lib.common_functions.file_functions.directory_to_files", "data")
    def test_append_csv_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            append_csv("non_existent", self.append_data)

    @patch("dsg_lib.common_functions.file_functions.directory_to_files", "data")
    def test_append_csv_header_mismatch(self):
        save_csv("test_append", self.test_data)
        mismatch_data = [
            ["Different", "Header"],
            ["John Doe", "jdoe@example.com"],
        ]
        with self.assertRaises(ValueError):
            append_csv("test_append", mismatch_data)

    @patch("dsg_lib.common_functions.file_functions.directory_to_files", "data")
    def test_append_csv_invalid_data_type(self):
        save_csv("test_append", self.test_data)
        with self.assertRaises(TypeError):
            append_csv("test_append", "not a list")
