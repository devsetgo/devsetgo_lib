# -*- coding: utf-8 -*-

import datetime
import unittest

import pytest

from dsg_lib.file_functions import create_sample_files
from dsg_lib.file_functions import open_csv
from dsg_lib.file_functions import open_json
from dsg_lib.file_functions import open_text

time_str = datetime.datetime.now()


class Test(unittest.TestCase):
    def test_create_sample_files(self):
        filename = "test_sample"
        samplesize = 10
        create_sample_files(filename, samplesize)

        file_named = "test_1.csv"
        result = open_csv(file_named)

        assert len(result) == samplesize - 1

    def test_open_json(self):
        file_named = "test_1.json"
        result = open_json(file_named)
        assert len(result) > 1
        assert isinstance(result, (list, dict))

    def test_open_json_no_file(self):
        file_named = "no_file_name.json"
        with pytest.raises(Exception):
            assert open_json(file_named)

    def test_open_json_exception_not_str(self):
        file_named = ["a", "list"]
        with pytest.raises(Exception):
            assert open_json(file_named)

    def test_open_json_exception_slash_win(self):
        file_named = "\this_is_not_right_json"
        with pytest.raises(Exception):
            assert open_json(file_named)

    def test_open_json_exception_slash_linux(self):
        file_named = "//this_is_not_right_json"
        with pytest.raises(Exception):
            assert open_json(file_named)

    def test_open_csv(self):
        file_named = "test_1.csv"
        result = open_csv(file_named)
        assert len(result) > 1

    def test_open_csv_quote_none(self):
        file_named = "test_1.csv"
        result = open_csv(file_name=file_named, quote_level="none")
        assert len(result) > 1

    # def test_open_csv_quote_non_numeric(self):
    #     file_named = "test_1.csv"
    #     result = open_csv(file_name=file_named, quote_level="non-numeric")
    #     assert len(result) > 1

    def test_open_csv_quote_minimal(self):
        file_named = "test_1.csv"
        result = open_csv(file_name=file_named, quote_level="minimal")
        assert len(result) > 1

    def test_open_csv_quote_all(self):
        file_named = "test_1.csv"
        result = open_csv(file_name=file_named, quote_level="all")
        assert len(result) > 1

    def test_open_csv_no_file(self):
        file_named = "no_file_name.csv"
        with pytest.raises(Exception):
            assert open_csv(file_named)

    def test_open_csv_exception_not_str(self):
        file_named = ["a", "list"]
        with pytest.raises(Exception):
            assert open_csv(file_named)

    def test_open_csv_exception_slash_win(self):
        file_named = "\this_is_not_right_csv"
        with pytest.raises(Exception):
            assert open_csv(file_named)

    def test_open_csv_exception_slash_linux(self):
        file_named = "//this_is_not_right_csv"
        with pytest.raises(Exception):
            assert open_csv(file_named)

    def test_open_csv_exception_file_name(self):
        file_named = ["a", "list"]
        with pytest.raises(Exception):
            assert open_csv(file_named)

    def test_open_csv_exception_quote_level(self):
        quote_level_wrong: str = "bob"
        file_named = "test_1.csv"
        with pytest.raises(ValueError):
            assert open_csv(file_name=file_named, quote_level=quote_level_wrong)

    def test_open_text(self):
        file_named = "test_1.html"
        result = open_text(file_named)
        assert "Test" in str(result)

    def test_open_txt_no_file(self):
        file_named = "no_file_name.html"
        with pytest.raises(Exception):
            assert open_text(file_named)

    def test_open_txt_exception_not_str(self):
        file_named = ["a", "list"]
        with pytest.raises(Exception):
            assert open_text(file_named)

    def test_open_txt_exception_slash_win(self):
        file_named = "\this_is_not_right_txt"
        with pytest.raises(Exception):
            assert open_text(file_named)

    def test_open_txt_exception_slash_linux(self):
        file_named = "//this_is_not_right_txt"
        with pytest.raises(Exception):
            assert open_text(file_named)
