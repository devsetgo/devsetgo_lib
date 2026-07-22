# -*- coding: utf-8 -*-
import os
import unittest
from tempfile import TemporaryDirectory
from unittest.mock import patch

from dsg_lib.common_functions.file_functions import open_json, save_json


class TestFileFunctions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open("data/json/test_file.json", "w") as f:
            f.write('{"key": "value"}')

    @classmethod
    def tearDownClass(cls):
        os.remove("data/json/test_file.json")

    @patch("dsg_lib.common_functions.file_functions.directory_to_files", "data")
    def test_open_json_with_valid_file(self):
        data = open_json("test_file.json")
        self.assertEqual(data, {"key": "value"})

    def test_open_json_with_invalid_file_name(self):
        with self.assertRaises(FileNotFoundError):
            open_json("invalid_file.json")

    def test_open_json_with_non_string_file_name(self):
        with self.assertRaises(TypeError):
            open_json(123)

    def test_open_json_round_trips_through_custom_root_folder(self):
        # A file saved via save_json(root_folder=...) must be readable back
        # via open_json(root_folder=...) -- this is the exact round-trip the
        # module previously could not do since open_json had no root_folder
        # parameter at all.
        with TemporaryDirectory() as tmp:
            save_json("roundtrip.json", {"key": "value"}, root_folder=tmp)
            data = open_json("roundtrip.json", root_folder=tmp)
            self.assertEqual(data, {"key": "value"})

    def test_open_json_with_root_folder_not_found(self):
        # root_folder must be honored precisely -- it should not silently
        # fall back to the default data/json directory.
        with TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                open_json("missing.json", root_folder=tmp)
