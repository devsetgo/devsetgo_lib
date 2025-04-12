# csv_example Example

# CSV Example Module

This module provides examples of how to work with CSV files using the `dsg_lib` library. It includes functions for saving data to a CSV file, opening and reading data from a CSV file, and creating sample files for testing purposes. The module is designed to demonstrate the usage of the `file_functions` and `logging_config` utilities provided by `dsg_lib`.

## Functions

### `save_some_data(example_list: list)`
Saves a list of data to a CSV file. The function uses the `save_csv` utility from `dsg_lib` to write the data to a file. The file is saved with a specified delimiter and quote character.

- **Parameters**:
  - `example_list` (list): A list of lists containing the data to be saved.
- **Notes**:
  - The file is saved in the `/data` directory with the name `your-file-name.csv`.
  - The delimiter used is `|`, and the quote character is `"`.
  - Refer to the `save_csv` documentation for additional options.

### `open_some_data(the_file_name: str) -> dict`
Opens a CSV file and returns its contents as a dictionary. This function assumes the CSV file has a header row and uses the `open_csv` utility from `dsg_lib`.

- **Parameters**:
  - `the_file_name` (str): The name of the CSV file to open.
- **Returns**:
  - `dict`: A dictionary representation of the CSV file's contents.
- **Notes**:
  - Additional options such as delimiter, quote level, and space handling can be configured.
  - Refer to the Python CSV documentation for more details: [Python CSV Documentation](https://docs.python.org/3/library/csv.html).

### `sample_files()`
Creates sample files for testing purposes. This function uses the `create_sample_files` utility from `dsg_lib`.

- **Notes**:
  - The sample file is named `test_sample` and contains 1000 rows of data.

## Example Usage

```python
if __name__ == "__main__":
    # Save example data to a CSV file
    save_some_data(example_list)

    # Open and read data from a CSV file
    opened_file = open_some_data("your-file-name.csv")
    print(opened_file)

    # Create sample files for testing
    sample_files()
```

## Logging

The module configures logging using the `config_log` utility from `dsg_lib`. The logging level is set to `DEBUG` to provide detailed information during execution.

## License
This module is licensed under the MIT License.

```python
from dsg_lib.common_functions.file_functions import (
    create_sample_files,
    open_csv,
    save_csv,
)
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
```
