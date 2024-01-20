# -*- coding: utf-8 -*-
import datetime
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from dsg_lib.folder_functions import get_directory_list

time_str = datetime.datetime.now(datetime.timezone.utc)


class TestGetDirectoryList(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for the tests
        self.test_dir = tempfile.mkdtemp()
        self.subdir1 = os.path.join(self.test_dir, "subdir1")
        self.subdir2 = os.path.join(self.test_dir, "subdir2")
        os.mkdir(self.subdir1)
        os.mkdir(self.subdir2)

    def tearDown(self):
        # Remove the temporary directory and its contents
        shutil.rmtree(self.test_dir)

    def test_get_directory_list(self):
        # Get the list of directories in the temporary directory
        dir_list = get_directory_list(self.test_dir)

        # Check that the list contains the expected directories
        self.assertEqual(len(dir_list), 2)
        self.assertIn(Path(self.subdir1), dir_list)
        self.assertIn(Path(self.subdir2), dir_list)

    def test_get_directory_list_nonexistent_dir(self):
        # Try to get the list of directories in a nonexistent directory
        dir_list = get_directory_list("nonexistent_dir")

        # Check that the function returns None
        self.assertIsNone(dir_list)
