import os
import unittest
from pathlib import Path
from unittest.mock import patch

from dsg_lib.file_functions import save_csv


class TestFileFunctions(unittest.TestCase):
    def setUp(self):
        self.test_data = [
            ["John Doe", "123 Main St", "jdoe@example.com"],
            ["Jane Smith", "456 Maple Ave", "jsmith@example.com"],
        ]
        self.csv_path = Path("data/csv/test_file.csv")
        if self.csv_path.exists():
            self.csv_path.unlink()

    def tearDown(self):
        if self.csv_path.exists():
            self.csv_path.unlink()

    @patch("dsg_lib.file_functions.directory_to_files", "data")
    def test_save_csv_with_valid_data(self):
        result = save_csv("test_file", self.test_data)
        self.assertEqual(result, "complete")
        self.assertTrue(self.csv_path.exists())

    @patch("dsg_lib.file_functions.directory_to_files", "data")
    def test_save_csv_with_invalid_data(self):
        with self.assertRaises(TypeError):
            save_csv("test_file", "not a list")

    @patch("dsg_lib.file_functions.directory_to_files", "data")
    def test_save_csv_with_invalid_file_name(self):
        with self.assertRaises(TypeError):
            save_csv("invalid/name", self.test_data)

    @patch("dsg_lib.file_functions.directory_to_files", "data")
    def test_save_csv_with_custom_delimiter(self):
        result = save_csv("test_file", self.test_data, delimiter=";")
        self.assertEqual(result, "complete")
        self.assertTrue(self.csv_path.exists())

    @patch("dsg_lib.file_functions.directory_to_files", "data")
    def test_save_csv_with_custom_quotechar(self):
        result = save_csv("test_file", self.test_data, quotechar="'")
        self.assertEqual(result, "complete")
        self.assertTrue(self.csv_path.exists())

    @patch("dsg_lib.file_functions.directory_to_files", "data")
    def test_save_csv_with_custom_root_folder(self):
        result = save_csv("test_file", self.test_data, root_folder="data/custom")
        self.assertEqual(result, "complete")
        custom_path = Path("data/custom/csv/test_file.csv")
        self.assertTrue(custom_path.exists())

    @patch("dsg_lib.file_functions.directory_to_files", "data")
    def test_save_csv_with_valid_data(self):
        result = save_csv("test_file", self.test_data)
        self.assertEqual(result, "complete")
        self.assertTrue(self.csv_path.exists())

        # Test invalid delimiter argument
        with self.assertRaises(TypeError):
            save_csv("test_file", self.test_data, delimiter="invalid")

        # Test invalid quotechar argument
        with self.assertRaises(TypeError):
            save_csv("test_file", self.test_data, quotechar="invalid")
