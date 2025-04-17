# csv_example Example

# CSV Example Module

This module provides examples of how to work with CSV files using the `dsg_lib` library. It includes functions for saving data to a CSV file, opening and reading data from a CSV file, appending data to an existing CSV file, deleting a CSV file, and creating sample files for testing purposes. The module is designed to demonstrate the usage of the `file_functions` and `logging_config` utilities provided by `dsg_lib`.

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

### `append_some_data(rows: list)`
Appends rows to an existing CSV file. The function uses the `append_csv` utility from `dsg_lib`.

- **Parameters**:
  - `rows` (list): A list of lists containing the rows to append. The header must match the existing file.

### `delete_example_file(file_name: str)`
Deletes a CSV file. The function uses the `delete_file` utility from `dsg_lib`.

- **Parameters**:
  - `file_name` (str): The name of the file to delete.

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
    print("Opened CSV data:", opened_file)

    # Append data to an existing CSV file
    rows_to_append = [
        ["thing_one", "thing_two"],  # header row (must match)
        ["i", "j"],
        ["k", "l"],
    ]
    append_some_data(rows_to_append)

    # Delete the CSV file
    delete_example_file("your-file-name.csv")

    # Create sample files for testing
    sample_files()
```

## Logging

The module configures logging using the `config_log` utility from `dsg_lib`. The logging level is set to `DEBUG` to provide detailed information during execution.

## License
This module is licensed under the MIT License.

```python
from typing import List, Dict, Any
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


def save_some_data(example_list: List[List[str]]) -> None:
    """
    Save a list of lists to a CSV file using dsg_lib's save_csv.

    Args:
        example_list (List[List[str]]): Data to save, including header as first row.
    """
    # Save data to CSV with custom delimiter and quote character
    save_csv(
        file_name="your-file-name.csv",
        data=example_list,
        root_folder="/data",
        delimiter="|",
        quotechar='"',
    )


def open_some_data(the_file_name: str) -> List[Dict[str, Any]]:
    """
    Open a CSV file and return its contents as a list of dictionaries.

    Args:
        the_file_name (str): Name of the CSV file to open.

    Returns:
        List[Dict[str, Any]]: List of rows as dictionaries.
    """
    result = open_csv(file_name=the_file_name)
    return result


def append_some_data(rows: List[List[str]]) -> None:
    """
    Append rows to an existing CSV file.

    Args:
        rows (List[List[str]]): Rows to append, header must match existing file.
    """
    from dsg_lib.common_functions.file_functions import append_csv
    append_csv(
        file_name="your-file-name.csv",
        data=rows,
        root_folder="/data",
        delimiter="|",
        quotechar='"',
    )


def delete_example_file(file_name: str) -> None:
    """
    Delete a CSV file using dsg_lib's delete_file.

    Args:
        file_name (str): Name of the file to delete.
    """
    from dsg_lib.common_functions.file_functions import delete_file
    delete_file(file_name)


def sample_files() -> None:
    """
    Create sample files for testing.
    """
    filename = "test_sample"
    samplesize = 1000
    create_sample_files(filename, samplesize)


if __name__ == "__main__":
    # Example: Save data to CSV
    save_some_data(example_list)

    # Example: Open and read data from CSV
    opened_file = open_some_data("your-file-name.csv")
    print("Opened CSV data:", opened_file)

    # Example: Append data to CSV (header must match)
    rows_to_append = [
        ["thing_one", "thing_two"],  # header row (must match)
        ["i", "j"],
        ["k", "l"],
    ]
    append_some_data(rows_to_append)

    # Example: Delete the CSV file
    delete_example_file("your-file-name.csv")

    # Example: Create sample files
    sample_files()
```
