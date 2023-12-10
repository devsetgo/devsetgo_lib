# -*- coding: utf-8 -*-
import datetime
import tempfile
import unittest

import pytest

from dsg_lib.file_functions import save_csv
from dsg_lib.file_functions import save_json
from dsg_lib.file_functions import save_text

time_str = datetime.datetime.now()


class Test(unittest.TestCase):
    def test_save_json(self):
        file_named = "test_1.json"
        json_data = []
        for _ in range(10):
            sample_dict = {"name": "bob", "date": str(time_str)}
            json_data.append(sample_dict)

        result = save_json(file_named, json_data)
        assert result == "complete"

    def test_save_json_custom_root(self):
        file_named = "test_1.json"
        json_data = []
        for _ in range(10):
            sample_dict = {"name": "bob", "date": str(time_str)}
            json_data.append(sample_dict)
        root_folder = tempfile.mktemp()
        result = save_json(file_named, json_data, root_folder=root_folder)
        assert result == "complete"

    def test_save_json_exception(tempfile):
        sample_str = "not a dict"
        file_named = "test_1_error.json"

        with pytest.raises(Exception):
            assert save_json(file_named, sample_str)

    def test_save_csv(tempfile):
        csv_data = []
        file_named = "test_1.csv"
        csv_data = []
        count = 0
        for _ in range(10):
            if count == 0:
                sample_dict = ["name", "date"]
            else:
                sample_dict = ["bob", str(datetime.datetime.now())]
            count += 1
            csv_data.append(sample_dict)

        result = save_csv(file_named, csv_data)
        assert result == "complete"

    def test_save_csv_exception_not_a_list(tempfile):
        csv_data = {
            "thing": 1,
            "thing2": "2",
        }
        file_named = "test_1.csv"

        with pytest.raises(TypeError):
            assert save_csv(file_named, csv_data)

    def test_save_csv_exception_delimiter(tempfile):
        csv_data = []
        file_named = "test_1.csv"
        csv_data = []
        count = 0
        for _ in range(10):
            if count == 0:
                sample_dict = ["name", "date"]
            else:
                sample_dict = ["bob", str(datetime.datetime.now())]
            count += 1
            csv_data.append(sample_dict)

        with pytest.raises(TypeError):
            assert save_csv(file_named, csv_data, delimiter="||")

    def test_save_csv_exception_quotechar(tempfile):
        csv_data = []
        file_named = "test_1.csv"
        csv_data = []
        count = 0
        for _ in range(10):
            if count == 0:
                sample_dict = ["name", "date"]
            else:
                sample_dict = ["bob", str(datetime.datetime.now())]
            count += 1
            csv_data.append(sample_dict)

        with pytest.raises(TypeError):
            assert save_csv(file_named, csv_data, quotechar="||")

    def test_save_text(tempfile):
        sample_html = """
                        <!DOCTYPE html>
                        <html>
                        <body>

                        <h1>This is a Test File</h1>

                        <p>Created by Pytest.</p>

                        </body>
                        </html>
                        """

        file_named = "test_1.html"

        result = save_text(file_named, sample_html)
        assert result == "complete"

    def test_save_text_exception(tempfile):
        sample_list = ["not a str"]
        file_named = "test_1_error.txt"

        with pytest.raises(Exception):
            assert save_text(file_named, sample_list)

    def test_save_csv_slash_exception(tempfile):
        csv_data = []
        file_named = r"test\_1.csv"
        csv_data = []
        count = 0
        for _ in range(10):
            if count == 0:
                sample_dict = ["name", "date"]
            else:
                sample_dict = ["bob", str(datetime.datetime.now())]
            count += 1
            csv_data.append(sample_dict)

        with pytest.raises(Exception):
            assert save_csv(file_named, csv_data)

    def test_save_text_slash_exception(tempfile):
        sample_str = "not a list"
        file_named = r"te/st_1_error.txt"

        with pytest.raises(Exception):
            assert save_text(file_named, sample_str)

    def test_save_json_slash_exception(tempfile):
        file_named = "tes/t_1.json"
        json_data = []
        for _ in range(10):
            sample_dict = {"name": "bob", "date": str(time_str)}
            json_data.append(sample_dict)

        with pytest.raises(Exception):
            assert save_json(file_named, json_data)
