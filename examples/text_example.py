# -*- coding: utf-8 -*-
"""
# Text Example Module

This module demonstrates basic file operations using the `dsg_lib.common_functions.file_functions` library.
It provides examples of saving text data to a file and reading text data from a file.

## Functions

### `save_some_data(example_text: str)`
Saves the provided text data to a file.
- **Parameters**:
  - `example_text` (str): The text data to be saved.
- **Behavior**:
  Calls the `save_text` function from `dsg_lib.common_functions.file_functions` to save the data to a file named `your-file-name.txt`.

### `open_some_data(the_file_name: str) -> str`
Reads text data from a specified file.
- **Parameters**:
  - `the_file_name` (str): The name of the file to be read.
- **Returns**:
  - `result` (str): The content of the file as a string.
- **Behavior**:
  Calls the `open_text` function from `dsg_lib.common_functions.file_functions` to read the content of the file.

### `save_csv_example(csv_data: list[list[str]], file_name: str = "example.csv")`
Saves example rows to a CSV file.
- **Parameters**:
  - `csv_data` (list[list[str]]): Rows for CSV (first row is header).
  - `file_name` (str): Target CSV file name.

### `open_csv_example(file_name: str = "example.csv") -> list[dict]`
Opens a CSV file and returns its content as a list of dictionaries.
- **Parameters**:
  - `file_name` (str): Name of the CSV file to read.
- **Returns**:
  - `list[dict]`: Parsed CSV rows.

### `save_json_example(data: dict | list, file_name: str = "example.json")`
Saves a dictionary or list as JSON.
- **Parameters**:
  - `data` (dict|list): Data to serialize.
  - `file_name` (str): Target JSON file name.

### `open_json_example(file_name: str = "example.json") -> dict | list`
Opens a JSON file and returns its content.
- **Parameters**:
  - `file_name` (str): Name of the JSON file to read.
- **Returns**:
  - `dict|list`: Parsed JSON content.

## Example Usage

```python
if __name__ == "__main__":
    save_some_data(example_text)
    opened_file: str = open_some_data("your-file-name.txt")
    print(opened_file)

    # CSV example
    csv_rows = [
        ["header1", "header2"],
        ["row1col1", "row1col2"]
    ]
    save_csv_example(csv_rows)
    print(open_csv_example())

    # JSON example
    json_obj = {"foo": "bar", "count": 1}
    save_json_example(json_obj)
    print(open_json_example())
```

## Notes
- Ensure that the `dsg_lib` library is installed and accessible in your environment.
- The file operations assume that the file paths and permissions are correctly configured.

## License
This module is licensed under the MIT License.
"""
from dsg_lib.common_functions.file_functions import (
    open_text, save_text,
    save_csv, open_csv,
    save_json, open_json
)

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


def save_csv_example(
    csv_data: list[list[str]],
    file_name: str = "example.csv"
) -> None:
    """
    Save example rows to a CSV file.

    Args:
        csv_data (list[list[str]]): Rows for CSV (first row is header).
        file_name (str): Target CSV file name.
    """
    # write rows out
    save_csv(file_name=file_name, data=csv_data)


def open_csv_example(
    file_name: str = "example.csv"
) -> list[dict]:
    """
    Open a CSV file and return its content as list of dicts.

    Args:
        file_name (str): Name of CSV to read.

    Returns:
        list[dict]: Parsed CSV rows.
    """
    return open_csv(file_name=file_name)


def save_json_example(
    data: dict | list,
    file_name: str = "example.json"
) -> None:
    """
    Save a dict or list as JSON.

    Args:
        data (dict|list): Data to serialize.
        file_name (str): Target JSON file name.
    """
    save_json(file_name=file_name, data=data)


def open_json_example(
    file_name: str = "example.json"
) -> dict | list:
    """
    Open a JSON file and return its content.

    Args:
        file_name (str): Name of JSON to read.

    Returns:
        dict|list: Parsed JSON content.
    """
    return open_json(file_name=file_name)


if __name__ == "__main__":
    save_some_data(example_text)
    opened_file: str = open_some_data("your-file-name.txt")
    print(opened_file)

    # CSV example
    csv_rows = [
        ["header1", "header2"],
        ["row1col1", "row1col2"]
    ]
    save_csv_example(csv_rows)
    print(open_csv_example())

    # JSON example
    json_obj = {"foo": "bar", "count": 1}
    save_json_example(json_obj)
    print(open_json_example())
