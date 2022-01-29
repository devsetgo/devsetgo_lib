# -*- coding: utf-8 -*-
import unittest

import pytest
from tqdm import tqdm

from dsg_lib.file_functions import open_csv

from dsg_lib.patterns import pattern_between_two_char

from .sample_data_for_tests import ASCII_LIST


class Test(unittest.TestCase):
    def test_pattern_between_two_char(self):
        char_list = []
        for char in ASCII_LIST:

            if char.isprintable() == True:
                char_list.append(char)

        err_list = []

        for l in char_list:
            for r in char_list:
                text = f"{l}found one{r} {l}found two{r}"
                data = pattern_between_two_char(text, l, r)

                if "Error" in data:
                    err_list.append(data)

        assert len(err_list) == 0

    def test_pattern_between_two_char_left_error(self):
        l = "["
        r = "\0"
        text = f"{l}found one{r}"

        data = pattern_between_two_char(text, l, r)
        assert "Error" in data

    def test_pattern_between_two_char_right_error(self):
        l = "\0"
        r = "]"
        text = f"{l}found one{r}"

        data = pattern_between_two_char(text, l, r)
        assert "Error" in data
