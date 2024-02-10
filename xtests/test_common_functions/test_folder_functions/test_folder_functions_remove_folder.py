# -*- coding: utf-8 -*-
import datetime
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from dsg_lib.folder_functions import remove_folder

# from dsg_lib.folder_functions import get_directory_list
# from dsg_lib.folder_functions import get_directory_list
# from dsg_lib.folder_functions import last_data_files_changed
# from dsg_lib.folder_functions import make_folder
# from dsg_lib.folder_functions import remove_folder


time_str = datetime.datetime.now(datetime.timezone.utc)


class TestRemoveFolder(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for the tests
        self.test_dir = tempfile.mkdtemp()
        self.test_subdir = os.path.join(self.test_dir, "test_subdir")
        os.mkdir(self.test_subdir)

    def tearDown(self):
        # Remove the temporary directory and its contents
        shutil.rmtree(self.test_dir)

    def test_remove_folder(self):
        # Remove the temporary subdirectory using the function
        remove_folder(self.test_subdir)

        # Check that the subdirectory no longer exists
        self.assertFalse(Path(self.test_subdir).exists())

    def test_remove_folder_nonexistent_dir(self):
        # Try to remove a nonexistent directory using the function
        with self.assertRaises(FileNotFoundError):
            remove_folder("nonexistent_dir")

    def test_remove_folder_nonempty_dir(self):
        # Create a temporary file in the subdirectory
        temp_file = os.path.join(self.test_subdir, "temp_file.txt")
        with open(temp_file, "w") as f:
            f.write("temp file")

        # Try to remove the subdirectory using the function
        with self.assertRaises(OSError):
            remove_folder(self.test_subdir)
