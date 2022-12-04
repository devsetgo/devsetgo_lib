# -*- coding: utf-8 -*-
from dsg_lib.file_functions import open_csv
from dsg_lib.file_functions import save_csv

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


if __name__ == "__main__":
    save_some_data(example_list)
    opened_file: dict = open_some_data("your-file-name.csv")
    print(opened_file)
