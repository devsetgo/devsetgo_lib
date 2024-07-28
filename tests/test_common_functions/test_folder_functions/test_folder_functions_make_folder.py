# -*- coding: utf-8 -*-
import shutil
import unittest
from datetime import datetime
from pathlib import Path

from dsg_lib.common_functions.folder_functions import make_folder

time_str = datetime.now()

# TODO: Improve Exception handling to check logging


class TestMakeFolder(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path("test_folder_make_folder")
        self.test_dir.mkdir()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_create_folder_successfully(self):
        # Create a new folder and check that it was created successfully
        new_folder = self.test_dir / "new_folder"
        self.assertTrue(make_folder(new_folder))
        self.assertTrue(new_folder.is_dir())

    def test_folder_already_exists(self):
        # Create a folder that already exists and check that an exception is raised
        existing_folder = self.test_dir
        with self.assertRaises(FileExistsError):
            make_folder(existing_folder)

    def test_folder_name_contains_invalid_characters(self):
        # Create a folder with an invalid name and check that an exception is raised
        invalid_folder_name = self.test_dir / "new<folder"
        with self.assertRaises(ValueError):
            make_folder(invalid_folder_name)
        self.assertFalse(invalid_folder_name.is_dir())
