# -*- coding: utf-8 -*-
"""
Author: Mike Ryan
Date: 2024/05/16
License: MIT
"""
from dsg_lib.common_functions.file_functions import create_sample_files, open_csv, save_csv
from dsg_lib.common_functions.logging_config import config_log

config_log(logging_level="DEBUG")

example_list = [
    ["thing_one", "thing_two"],
    ["a", "b"],
    ["c", "d"],
    ["e", "f"],
    ["g", "h"],
]


def save_some_data(example_list: list):
    # function requires file_name and data list to be sent.
    # see documentation for additonal information
    save_csv(
        file_name="your-file-name.csv",
        data=example_list,
        root_folder="/data",
        delimiter="|",
        quotechar='"',
    )


def open_some_data(the_file_name: str) -> dict:
    """
    function requires file_name and a dictionary will be returned
    this function is designed with the idea that the CSV file has a header row.
    see documentation for additonal information
    options
        file_name: str | "myfile.csv"
        delimit: str | example - ":" single character only inside quotes
        quote_level:str | ["none","non-numeric","minimal","all"] default is minimal
        skip_initial_space:bool | default is True
    See Python documentation as needed https://docs.python.org/3/library/csv.html
    """

    result: dict = open_csv(file_name=the_file_name)
    return result


def sample_files():
    filename = "test_sample"
    samplesize = 1000
    create_sample_files(filename, samplesize)


if __name__ == "__main__":
    # save_some_data(example_list)
    # opened_file: dict = open_some_data("your-file-name.csv")
    # print(opened_file)
    sample_files()
