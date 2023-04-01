# import os
# import shutil
# import unittest
# from unittest.mock import patch

# from dsg_lib import file_functions


import os
from pathlib import Path

import pytest

from dsg_lib.file_functions import open_text

directory_to_files = "data"


def test_open_text_file():
    file_name = "test.txt"
    file_contents = "This is a test file."
    file_path = os.path.join(directory_to_files, "text", file_name)

    # Create test file
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(file_contents)

    # Test function
    result = open_text(file_name)
    assert result == file_contents


def test_open_text_invalid_file_name():
    invalid_file_name = "invalid/file/name.txt"

    # Test function
    with pytest.raises(TypeError):
        open_text(invalid_file_name)


def test_open_text_nonexistent_file():
    nonexistent_file_name = "nonexistent.txt"

    # Test function
    with pytest.raises(FileNotFoundError):
        open_text(nonexistent_file_name)


def test_open_text_integer_file_name():
    integer_file_name = 12345

    # Test function
    with pytest.raises(TypeError):
        open_text(integer_file_name)
