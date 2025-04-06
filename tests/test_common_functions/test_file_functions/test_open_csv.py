# -*- coding: utf-8 -*-
import os
import unittest
from unittest.mock import patch

from dsg_lib.common_functions.file_functions import open_csv


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
