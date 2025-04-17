# -*- coding: utf-8 -*-
"""
test_file_functions.py

This module contains unit tests for the `file_functions` module in the
`dsg_lib.common_functions` package.

Tests:
    - test_save_json_appends_extension: Tests that the `save_json` function
      appends the `.json` extension to the file name if it is missing.

Author: Mike Ryan
Date: 2024/05/16
License: MIT
"""

from dsg_lib.common_functions import file_functions


def test_save_json_appends_extension(tmp_path):
    """
    Test that the `save_json` function appends the `.json` extension to the file
    name if it is missing.
    """
    data = {"foo": "bar"}
    file_name = "mytestfile"  # No .json extension
    result = file_functions.save_json(file_name, data, root_folder=str(tmp_path))
    expected_file = tmp_path / "mytestfile.json"
    assert expected_file.exists()
    assert result == "File saved successfully"
    # Optionally, check file contents
    with open(expected_file) as f:
        import json

        assert json.load(f) == data
