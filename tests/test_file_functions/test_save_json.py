# -*- coding: utf-8 -*-

# import json
# import os
# import unittest
# from unittest.mock import patch

# from dsg_lib.file_functions import save_json


# class TestSaveJson(unittest.TestCase):
#     def setUp(self):
#         self.data_dir = "./data_test"
#         os.makedirs(self.data_dir, exist_ok=True)

#     def tearDown(self):
#         os.system(f"rm -rf {self.data_dir}")

#     def test_save_json_creates_file(self):
#         # Arrange
#         file_name = "test_file"
#         data = {"name": "John", "age": 30}
#         file_path = os.path.join(self.data_dir, "json", file_name + ".json")

#         # Act
#         result = save_json(file_name, data, root_folder=self.data_dir)

#         # Assert
#         self.assertEqual(result, "File saved successfully")
#         self.assertTrue(os.path.exists(file_path))

#         # Cleanup
#         os.remove(file_path)

#     def test_save_json_with_list(self):
#         # Arrange
#         file_name = "test_file"
#         data = [1, 2, 3]
#         file_path = os.path.join(self.data_dir, "json", file_name + ".json")

#         # Act
#         result = save_json(file_name, data, root_folder=self.data_dir)

#         # Assert
#         self.assertEqual(result, "File saved successfully")
#         self.assertTrue(os.path.exists(file_path))

#         # Cleanup
#         os.remove(file_path)

#     def test_save_json_with_invalid_data_type(self):
#         # Arrange
#         file_name = "test_file"
#         data = "not a list or dict"

#         # Act and Assert
#         with self.assertRaises(TypeError):
#             save_json(file_name, data, root_folder=self.data_dir)

#     def test_save_json_with_invalid_file_name(self):
#         # Arrange
#         file_name = "invalid/file/name"
#         data = {"name": "John", "age": 30}

#         # Act and Assert
#         with self.assertRaises(ValueError):
#             save_json(file_name, data, root_folder=self.data_dir)

#     def test_save_json_with_unrecognized_file_type(self):
#         # Arrange
#         file_name = "test_file"
#         data = {"name": "John", "age": 30}
#         file_type = "invalid_file_type"

#         # Act and Assert
#         with self.assertRaises(ValueError):
#             save_json(file_name, data, file_type=file_type, root_folder=self.data_dir)

#     def test_save_json_raises_exception_on_failure(self):
#         # Arrange
#         file_name = "test_file"
#         data = {"name": "John", "age": 30}

#         with patch("json.dump") as mock_json_dump:
#             mock_json_dump.side_effect = Exception("Error in writing file")

#             # Act and Assert
#             with self.assertRaises(Exception):
#                 save_json(file_name, data, root_folder=self.data_dir)
from dsg_lib.file_functions import save_json

import unittest
from pathlib import Path
import shutil
from typing import List, Dict


class TestSaveJson(unittest.TestCase):
    def setUp(self) -> None:
        # Define test data
        self.valid_file_name = "test.json"
        self.invalid_file_name = "test/invalid.json"
        self.test_data = {"id": 1, "name": "Test"}

    def test_success_save_json(self):
        # Test successful save of JSON file
        result = save_json(self.valid_file_name, self.test_data)
        self.assertEqual(result, "File saved successfully")
        file_path = Path("data/json") / self.valid_file_name
        self.assertTrue(file_path.exists())

    def test_invalid_file_name(self):
        # Test raise error when file name contains forward slash or backslash
        with self.assertRaises(ValueError):
            save_json(self.invalid_file_name, self.test_data)

    def test_invalid_data_type(self):
        # Test raise error when data is not list or dictionary
        invalid_data = "test"
        with self.assertRaises(TypeError):
            save_json(self.valid_file_name, invalid_data)

    def tearDown(self) -> None:
        # Remove created test files
        file_path = Path("data/json") / self.valid_file_name
        if file_path.exists():
            file_path.unlink()
        # shutil.rmtree(Path("data/json"))
