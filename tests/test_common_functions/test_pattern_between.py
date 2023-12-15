# -*- coding: utf-8 -*-
import unittest

import pytest
from tqdm import tqdm

from dsg_lib.functions.file_functions import open_csv
from dsg_lib.functions.patterns import pattern_between_two_char

# from .sample_data_for_tests import ASCII_LIST
from ..sample_data_for_tests import ASCII_LIST


class TestPatternBetweenTwoChar(unittest.TestCase):
    def test_pattern_between_two_char_empty_characters(self):
        with self.assertRaises(ValueError):
            pattern_between_two_char(
                text_string="abc<one>123<two>456<three>",
                left_characters="",
                right_characters="",
            )

    def test_pattern_between_two_char_integer_input(self):
        with pytest.raises(TypeError):
            pattern_between_two_char(
                text_string=123, left_characters="<", right_characters=">"
            )

    def test_pattern_between_two_char_valid_input(self):
        result = pattern_between_two_char(
            text_string="abc<one>123<two>456<three>",
            left_characters="<",
            right_characters=">",
        )

        assert result["found"] == ["one", "two", "three"]
        assert result["matched_found"] == 3
        assert result["pattern_parameters"]["left_character"] == "<"
        assert result["pattern_parameters"]["right_character"] == ">"
        # assert result["pattern_parameters"]["regex_pattern"] == "<(.+?)\>"
        assert result["pattern_parameters"]["regex_pattern"] is not None
        assert (
            result["pattern_parameters"]["text_string"] == "abc<one>123<two>456<three>"
        )

    def test_pattern_between_two_char_edge_cases(self):
        # test with very long input string
        long_input = "xyz" * 10000
        long_text = f"{long_input}abc<one>123<two>456<three>{long_input}"
        result = pattern_between_two_char(
            text_string=long_text, left_characters="<", right_characters=">"
        )
        assert result["found"] == ["one", "two", "three"]
        assert result["matched_found"] == 3
        assert len(result["pattern_parameters"]["text_string"]) > 20000

        # test with special characters in input string
        result = pattern_between_two_char(
            text_string="*c]", left_characters="*", right_characters="]"
        )
        print(result)
        assert result["found"] == ["c\\"]
