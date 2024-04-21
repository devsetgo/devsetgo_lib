# -*- coding: utf-8 -*-

import unittest
from pathlib import Path

from dsg_lib.common_functions.file_functions import save_json


class TestSaveJson(unittest.TestCase):
    def setUp(self) -> None:
        # Define test data
        self.valid_file_name = 'test.json'
        self.invalid_file_name = 'test/invalid.json'
        self.test_data = {'id': 1, 'name': 'Test'}

    def test_success_save_json(self):
        # Test successful save of JSON file
        result = save_json(self.valid_file_name, self.test_data)
        self.assertEqual(result, 'File saved successfully')
        file_path = Path('data/json') / self.valid_file_name
        self.assertTrue(file_path.exists())

    def test_invalid_file_name(self):
        # Test raise error when file name contains forward slash or backslash
        with self.assertRaises(ValueError):
            save_json(self.invalid_file_name, self.test_data)

    def test_invalid_data_type(self):
        # Test raise error when data is not list or dictionary
        invalid_data = 'test'
        with self.assertRaises(TypeError):
            save_json(self.valid_file_name, invalid_data)

    def tearDown(self) -> None:
        # Remove created test files
        file_path = Path('data/json') / self.valid_file_name
        if file_path.exists():
            file_path.unlink()
        # shutil.rmtree(Path("data/json"))
