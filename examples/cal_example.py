# -*- coding: utf-8 -*-
from dsg_lib.calendar_functions import get_month

month_list: list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]


def calendar_check():
    for i in month_list:
        month = get_month(month=i)
        print(month)


if __name__ == "__main__":
    calendar_check()
