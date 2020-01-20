# -*- coding: utf-8 -*-
import os
import time
import unittest
from datetime import date
from datetime import datetime
from pathlib import Path

import pytest

from com_lib.folder_functions import get_directory_list
from com_lib.folder_functions import last_data_files_changed
from com_lib.folder_functions import make_folder
from com_lib.folder_functions import remove_folder

time_str = datetime.now()

# TODO: Improve Exception handling to check logging


class Test(unittest.TestCase):
    def test_make_folder(self):

        directory_to__files: str = "data"
        file_directory = f"{directory_to__files}/x"
        directory_path = Path.cwd().joinpath(file_directory)
        make_folder(directory_path)
        assert os.path.isdir(directory_path) == True
        remove_folder(directory_path)

    def test_directory_list(self):

        date_object = date.today()
        year = date_object.strftime("%Y")
        directory = get_directory_list("data")
        file_dir = []
        for i in directory:
            dir_name = str(i)
            if year in dir_name:
                file_dir.append(dir_name)
        assert len(file_dir) <= 1

    def test_get_directory_list_error(self):

        directory_to__files: str = "a_non_existent_folder"
        directory_path = Path.cwd().joinpath(directory_to__files)
        with pytest.raises(Exception):
            assert get_directory_list(directory_path)

    def test_last_data_files_changed(self):

        date_object = date.today()
        year = date_object.strftime("%Y")
        directory_to__files: str = "data"
        directory_path = Path.cwd().joinpath(directory_to__files)
        time_stamp, file_path = last_data_files_changed(directory_path)

        assert str(year) in str(time_stamp)

    def test_last_data_files_changed_exception(self):

        directory_to__files: str = "a_non_existent_folder"
        directory_path = Path.cwd().joinpath(directory_to__files)
        with pytest.raises(Exception):
            assert last_data_files_changed(directory_path)

    def test_remove_folder(tmpdir):

        directory_to__files: str = "data"
        file_directory = f"{directory_to__files}/{tmpdir}"
        directory_path = Path.cwd().joinpath(file_directory)
        make_folder(directory_path)
        time.sleep(1)
        remove_folder(directory_path)
        assert directory_path.is_dir() == False

    def test_remove_folder_exception(self):

        directory_to__files: str = "data"
        file_directory = f"{directory_to__files}/bob"
        directory_path = Path.cwd().joinpath(file_directory)
        with pytest.raises(Exception):
            assert remove_folder(directory_path)
