# -*- coding: utf-8 -*-
import os
import unittest
from tempfile import TemporaryDirectory
from unittest.mock import patch

from dsg_lib.common_functions.file_functions import open_csv, save_csv


class TestOpenCsv(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.makedirs("data/csv", exist_ok=True)
        with open("data/csv/test_file.csv", "w", encoding="utf-8") as f:
            f.write("col1,col2,col3\n1,2,3\n4,5,6\n")

    @classmethod
    def tearDownClass(cls):
        os.remove("data/csv/test_file.csv")

    @patch("dsg_lib.common_functions.file_functions.directory_to_files", "data")
    def test_open_csv_with_valid_file(self):
        # Updated to include '.csv'
        data = open_csv("test_file.csv")
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["col1"], "1")
        self.assertEqual(data[0]["col2"], "2")
        self.assertEqual(data[0]["col3"], "3")
        self.assertEqual(data[1]["col1"], "4")
        self.assertEqual(data[1]["col2"], "5")
        self.assertEqual(data[1]["col3"], "6")

    @patch("dsg_lib.common_functions.file_functions.directory_to_files", "data")
    def test_open_csv_with_invalid_file(self):
        with self.assertRaises(FileNotFoundError):
            open_csv("non_existent_file")

    def test_open_csv_with_invalid_file_name_type(self):
        with self.assertRaises(TypeError):
            open_csv(123)

    def test_open_csv_with_invalid_quote_level(self):
        with self.assertRaises(ValueError):
            open_csv("test_file", quote_level="invalid")

    def test_open_csv_with_delimiter_and_quotechar(self):
        with self.assertRaises(TypeError):
            open_csv("test_file", delimiter=",", quote_level="minimal", quotechar='"')

    def test_open_csv_with_invalid_delimiter_type(self):
        with self.assertRaises(TypeError):
            open_csv("test_file", delimiter="abc")

    def test_open_csv_with_quotechar_length_greater_than_one(self):
        with self.assertRaises(TypeError):
            open_csv("test_file", quotechar="abc")

    def test_open_csv_round_trips_through_custom_root_folder(self):
        # A file saved via save_csv(root_folder=...) must be readable back
        # via open_csv(root_folder=...) -- previously open_csv had no
        # root_folder parameter at all.
        with TemporaryDirectory() as tmp:
            save_csv(
                "roundtrip.csv", [["col1", "col2"], ["1", "2"]], root_folder=tmp
            )
            data = open_csv("roundtrip.csv", root_folder=tmp)
            self.assertEqual(data, [{"col1": "1", "col2": "2"}])

    def test_open_csv_with_root_folder_not_found(self):
        # root_folder must be honored precisely -- it should not silently
        # fall back to the default data/csv directory.
        with TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                open_csv("missing.csv", root_folder=tmp)
