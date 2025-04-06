# -*- coding: utf-8 -*-
"""
Author: Mike Ryan
Date: 2024/05/16
License: MIT
"""
import time
from datetime import datetime
from dsg_lib.common_functions.file_functions import save_csv
from dsg_lib.common_functions.logging_config import config_log
import random

config_log(logging_level="DEBUG")

example_list = [
    ["thing_one", "thing_two"],
    ["a", "b"],
    ["c", "d"],
    ["e", "f"],
    ["g", "h"],
]


def create_sample_list(qty=10):
    """
    Create a sample list of lists with specified quantity.
    """
    headers = ["thing_one", "thing_two", "thing_three", "thing_four", "thing_five"]
    sample_list = [headers]
    for i in range(qty):
        sample_list.append(
            [f"item_{i+1}", f"item_{i+2}", f"item_{i+3}", f"item_{i+4}", f"item_{i+5}"]
        )
    return sample_list


def save_data_with_timer():
    """
    Saves a new CSV file every 5 seconds with a unique timestamped name.
    """
    while True:
        example_list = create_sample_list(qty=random.randint(10, 100000))
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"data_{timestamp}.csv"
        save_csv(
            file_name=file_name,
            data=example_list,
            root_folder="/workspaces/devsetgo_lib/data/move/source",
            delimiter="|",
            quotechar='"',
        )
        print(f"Saved file: {file_name}")
        time.sleep(5)


if __name__ == "__main__":
    save_data_with_timer()
