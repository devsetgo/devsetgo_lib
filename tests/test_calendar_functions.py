# -*- coding: utf-8 -*-
import datetime
import unittest
import tempfile
import pytest
from devsetgo_lib.calendar_functions import get_month


class Test(unittest.TestCase):
    def test_valid_months(self):

        month_list: list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        for i in month_list:
            result = get_month(month=i)
            assert result != "Invalid month number"

    def test_invalid_months(self):

        month_list: list = [0, 13]
        for i in month_list:
            result = get_month(month=i)
            assert result == "Invalid month number"
