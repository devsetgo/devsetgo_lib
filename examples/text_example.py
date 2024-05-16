# -*- coding: utf-8 -*-
"""
Author: Mike Ryan
Date: 2024/05/16
License: MIT
"""
from dsg_lib.common_functions.file_functions import open_text, save_text

example_text = """
<!DOCTYPE html>
<html>
<head>
<title>Page Title</title>
</head>
<body>

<h1>This is a Heading</h1>
<p>This is a paragraph.</p>

</body>
</html>
 """


def save_some_data(example_text: str):
    # function requires file_name and data as a string to be sent.
    # see documentation for additonal information
    save_text(file_name="your-file-name.txt", data=example_text)


def open_some_data(the_file_name: str) -> str:
    # function requires file_name and a string will be returned
    # see documentation for additonal information
    result: str = open_text(file_name=the_file_name)
    return result


if __name__ == "__main__":
    save_some_data(example_text)
    opened_file: str = open_some_data("your-file-name.txt")
    print(opened_file)
