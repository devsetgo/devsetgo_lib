# -*- coding: utf-8 -*-
import os
import time
import unittest
from datetime import date
from datetime import datetime
from pathlib import Path

import pytest
from dsg_lib.folder_functions import get_directory_list
from dsg_lib.folder_functions import last_data_files_changed
from dsg_lib.folder_functions import make_folder
from dsg_lib.folder_functions import remove_folder

import shutil

time_str = datetime.now()

# TODO: Improve Exception handling to check logging


class Test(unittest.TestCase):
    def test_remove_folder(self):

        directory_to__files: str = "data"
        file_directory = f"{directory_to__files}"
        directory_path = Path.cwd().joinpath(file_directory)
        shutil.rmtree(directory_path)

        # remove_folder(directory_path)
        assert directory_path.is_dir() == False
