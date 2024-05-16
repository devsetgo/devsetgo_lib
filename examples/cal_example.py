# -*- coding: utf-8 -*-
"""
Author: Mike Ryan
Date: 2024/05/16
License: MIT
"""
from dsg_lib.common_functions import calendar_functions

month_list: list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
month_names: list = [
    "january",
    "february",
    "march",
    "april",
    "may",
    "june",
    "july",
    "august",
    "september",
    "october",
    "november",
    "december",
    "bob",
]


def calendar_check_number():
    for i in month_list:
        month = calendar_functions.get_month(month=i)
        print(month)


def calendar_check_name():
    for i in month_names:
        month = calendar_functions.get_month_number(month_name=i)
        print(month)


if __name__ == "__main__":
    calendar_check_number()
    calendar_check_name()
