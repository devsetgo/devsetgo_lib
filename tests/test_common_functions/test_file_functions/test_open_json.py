# -*- coding: utf-8 -*-
import os
import unittest
from unittest.mock import patch

from dsg_lib.functions.file_functions import open_json


class TestFileFunctions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open("data/json/test_file.json", "w") as f:
            f.write('{"key": "value"}')

    @classmethod
    def tearDownClass(cls):
        os.remove("data/json/test_file.json")

    @patch("dsg_lib.functions.file_functions.directory_to_files", "data")
    def test_open_json_with_valid_file(self):
        data = open_json("test_file.json")
        self.assertEqual(data, {"key": "value"})

    def test_open_json_with_invalid_file_name(self):
        with self.assertRaises(FileNotFoundError):
            open_json("invalid_file.json")

    def test_open_json_with_non_string_file_name(self):
        with self.assertRaises(TypeError):
            open_json(123)
