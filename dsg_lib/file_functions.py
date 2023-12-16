# -*- coding: utf-8 -*-
"""
file_functions.py

This module provides a function to delete a file with a specified name from a
specified directory.

Functions:
    delete_file(file_name: str) -> str:
        Deletes a file with the specified file name from the directory specified
        by the `directory_to_files` variable. The file type is determined by the
        file extension, and the file is deleted from the subdirectory
        corresponding to the file type.

        Args:
            file_name (str): The name of the file to be deleted.

        Returns:
            str: A string indicating that the file has been deleted.

        Raises:
            TypeError: If the file name is not a string. ValueError: If the file
            name contains a forward slash or backslash, or if the file type is
            not supported. FileNotFoundError: If the file does not exist.

Example: ```python from dsg_lib import file_functions
file_functions.delete_file("test.csv")  # Outputs: 'complete' ```
"""

# Import required modules
import csv
import json
import os
import random
from datetime import datetime
from pathlib import Path
from typing import List

from loguru import logger

# Set the path to the directory where the files are located
directory_to_files: str = "data"

# A dictionary that maps file types to directories
directory_map = {".csv": "csv", ".json": "json", ".txt": "text"}


def delete_file(file_name: str) -> str:
    """
    Deletes a file with the specified file name from the specified directory.
    The file type is determined by the file extension.

    Args:
        directory_to_files (str): The directory where the file is located.
        file_name (str): The name of the file to be deleted.

    Returns:
        str: A message indicating whether the file has been deleted successfully
        or an error occurred.

    Raises:
        TypeError: If the directory or file name is not a string. ValueError: If
        the file name contains a forward slash or backslash, or if the file type
        is not supported. FileNotFoundError: If the file does not exist.

    Example: ```python from dsg_lib import file_functions
    file_functions.delete_file("test.csv")  # Outputs: 'File deleted
    successfully' ```
    """
    logger.info(f"Deleting file: {file_name}")

    # Check that the file name is a string
    if not isinstance(file_name, str):
        raise TypeError(f"{file_name} is not a valid string")

    # Split the file name into its name and extension components
    file_name, file_ext = os.path.splitext(file_name)

    # Check that the file name does not contain a forward slash or backslash
    if os.path.sep in file_name:
        raise ValueError(f"{file_name} cannot contain {os.path.sep}")

    # Check that the file type is supported
    if file_ext not in directory_map:
        raise ValueError(
            f"unsupported file type: {file_ext}. Supported file types are: {', '.join(directory_map.keys())}"
        )

    # Construct the full file path
    file_directory = Path.cwd() / directory_to_files / directory_map[file_ext]
    file_path = file_directory / f"{file_name}{file_ext}"

    # Check that the file exists
    if not file_path.is_file():
        raise FileNotFoundError(f"file not found: {file_name}{file_ext}")

    # Delete the file
    os.remove(file_path)
    logger.info(f"File {file_name}{file_ext} deleted from file path: {file_path}")

    # Return a string indicating that the file has been deleted
    return "complete"


def save_json(file_name: str, data, root_folder: str = None) -> str:
    """
    Saves a dictionary or a list as a JSON file with the specified file name in
    the specified directory.

    Args:
        file_name (str): The name of the file to save the data in. Should
        include the '.json' extension. data (list or dict): The data to be
        saved. root_folder (str, optional): The root directory where the file
        will be saved. Defaults to None, which means the file will be saved in
        the 'data' directory.

    Returns:
        str: A message indicating whether the file has been saved successfully
        or an error occurred.

    Raises:
        TypeError: If the data is not a list or a dictionary, or the file name
        or directory is not a string. ValueError: If the file name contains a
        forward slash or backslash, or if the file name does not end with
        '.json'.

    Example: ```python from dsg_lib import file_functions data = {"key":
    "value"} file_functions.save_json("test.json", data, "/path/to/directory")
    # Saves data to '/path/to/directory/test.json' ```
    """
    try:
        # Validate inputs
        if not isinstance(data, (list, dict)):
            raise TypeError(
                f"data must be a list or a dictionary instead of type {type(data)}"
            )
        if "/" in file_name or "\\" in file_name:
            raise ValueError(f"{file_name} cannot contain / or \\")

        # Add extension if not present in file_name
        if not file_name.endswith(".json"):  # pragma: no cover
            file_name += ".json"  # pragma: no cover

        if root_folder is None:
            root_folder = directory_to_files

        # Determine directory
        json_directory = Path(root_folder) / "json"

        # Construct file path
        file_path = json_directory / file_name

        # Create the json directory if it does not exist
        json_directory.mkdir(parents=True, exist_ok=True)

        # Write data to file
        with open(file_path, "w") as write_file:
            json.dump(data, write_file)

        # Log success message
        logger.info(f"File created: {file_path}")

        return "File saved successfully"

    except (TypeError, ValueError) as e:
        logger.error(f"Error creating file {file_name}: {e}")
        raise


def open_json(file_name: str) -> dict:
    """
    Open a JSON file and load its contents into a dictionary.

    Args:
        file_name (str): The name of the JSON file to open.

    Returns:
        dict: The contents of the JSON file as a dictionary.

    Raises:
        TypeError: If the file name is not a string. FileNotFoundError: If the
        file does not exist.
    """
    # Check if file name is a string
    if not isinstance(file_name, str):
        error = f"{file_name} is not a valid string"
        logger.error(error)
        raise TypeError(error)

    file_directory = Path(directory_to_files) / directory_map[".json"]
    file_save = file_directory / file_name

    # Check if path correct
    if not file_save.is_file():
        error = f"file not found error: {file_save}"
        logger.exception(error)
        raise FileNotFoundError(error)

    # open file
    with open(file_save) as read_file:
        # load file into data variable
        result = json.load(read_file)

    logger.info(f"File Opened: {file_name}")
    return result


# CSV File Processing TODO: Append CSV


def save_csv(
    file_name: str,
    data: list,
    root_folder: str = None,
    delimiter: str = ",",
    quotechar: str = '"',
) -> str:
    """
    Saves a list of dictionaries as a CSV file with the specified file name in
    the specified directory. Each dictionary in the list should represent a row
    in the CSV file.

    Args:
        file_name (str): The name of the file to save the data in. Should
        include the '.csv' extension. data (list): The data to be saved. Each
        element of the list should be a dictionary where the keys are column
        names and the values are the data for those columns. root_folder (str,
        optional): The root directory where the file will be saved. If None, the
        file will be saved in the current directory. Defaults to None. delimiter
        (str, optional): The character used to separate fields in the CSV file.
        Defaults to ','. quotechar (str, optional): The character used to quote
        fields in the CSV file. Defaults to '"'.

    Returns:
        str: A message indicating whether the file has been saved successfully
        or an error occurred.

    Raises:
        TypeError: If the data is not a list, or the file name, delimiter, or
        quotechar is not a string. ValueError: If the file name does not end
        with '.csv'.

    Example: ```python from dsg_lib import file_functions data = [{"column1":
    "value1", "column2": "value2"}] file_functions.save_csv("test.csv", data,
    "/path/to/directory", delimiter=";", quotechar="'")  # Saves data to
    '/path/to/directory/test.csv' ```
    """
    # Set the root folder to directory_to_files if None
    if root_folder is None:
        root_folder = directory_to_files

    # Create the csv directory if it does not exist
    csv_directory = Path(root_folder) / "csv"
    csv_directory.mkdir(parents=True, exist_ok=True)

    # Check that delimiter and quotechar are single characters
    if len(delimiter) != 1:
        raise TypeError(f"{delimiter} can only be a single character")
    if len(quotechar) != 1:
        raise TypeError(f"{quotechar} can only be a single character")

    # Check that data is a list
    if not isinstance(data, list):
        raise TypeError(f"{data} is not a valid list")

    # Check that file_name is a string and does not contain invalid characters
    if not isinstance(file_name, str) or "/" in file_name or "\\" in file_name:
        raise TypeError(f"{file_name} is not a valid file name")

    # Add extension to file_name if needed
    if not file_name.endswith(".csv"):
        file_name += ".csv"

    # Create the file path
    file_path = csv_directory / file_name

    # Write data to file
    with open(file_path, "w", encoding="utf-8", newline="") as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=delimiter, quotechar=quotechar)
        csv_writer.writerows(data)

    logger.info(f"File Create: {file_name}")
    return "complete"


def open_csv(
    file_name: str,
    delimiter: str = ",",
    quote_level: str = "minimal",
    skip_initial_space: bool = True,
) -> list:
    """
    Opens a CSV file with the specified file name and returns its contents as a
    list of dictionaries.

    Args:
        file_name (str): The name of the file to open. Should include the '.csv'
        extension. delimiter (str, optional): The character used to separate
        fields in the CSV file. Defaults to ','. quote_level (str, optional):
        The quoting level used in the CSV file. Valid levels are "none",
        "minimal", and "all". Defaults to "minimal". skip_initial_space (bool,
        optional): Whether to skip initial whitespace in the CSV file. Defaults
        to True.

    Returns:
        list: The contents of the CSV file as a list of dictionaries. Each
        dictionary represents a row in the CSV file, where the keys are column
        names and the values are the data for those columns.

    Raises:
        TypeError: If `file_name` is not a string. ValueError: If `quote_level`
        is not a valid level. FileNotFoundError: If the file does not exist.

    Example: ```python from dsg_lib import file_functions data =
    file_functions.open_csv("test.csv", delimiter=";", quote_level="all",
    skip_initial_space=False)  # Returns: [{'column1': 'value1', 'column2':
    'value2'}] ```
    """
    # A dictionary that maps quote levels to csv quoting constants
    quote_levels = {
        "none": csv.QUOTE_NONE,
        "minimal": csv.QUOTE_MINIMAL,
        "all": csv.QUOTE_ALL,
    }

    # Check that file name is a string
    if not isinstance(file_name, str):
        error = f"{file_name} is not a valid string"
        logger.error(error)
        raise TypeError(error)

    # Check that quote level is valid
    quote_level = quote_level.lower()
    if quote_level not in quote_levels:
        error = f"Invalid quote level: {quote_level}. Valid levels are: {', '.join(quote_levels)}"
        logger.error(error)
        raise ValueError(error)
    quoting = quote_levels[quote_level]

    # Add extension to file name and create file path
    file_name = f"{file_name}.csv"
    file_directory = Path.cwd().joinpath(directory_to_files).joinpath("csv")
    file_path = file_directory.joinpath(file_name)

    # Check that file exists
    if not file_path.is_file():
        error = f"File not found: {file_path}"
        logger.error(error)
        raise FileNotFoundError(error)

    # Read CSV file
    data = []
    with file_path.open(encoding="utf-8") as f:
        reader = csv.DictReader(
            f,
            delimiter=delimiter,
            quoting=quoting,
            skipinitialspace=skip_initial_space,
        )
        for row in reader:
            data.append(dict(row))

    logger.info(f"File opened: {file_name}")
    return data


# A list of first names to randomly select from
first_name: List[str] = [
    "Amy",
    "Adam",
    "Catherine",
    "Charlotte",
    "Charles",
    "Craig",
    "Deloris",
    "Doris",
    "Donna",
    "Eugene",
    "Eileen",
    "Emma",
    "Gerald",
    "Geraldine",
    "Gordon",
    "Jack",
    "Jenny",
    "Kelly",
    "Kevin",
    "Linda",
    "Lyle",
    "Michael",
    "Monica",
    "Nancy",
    "Noel",
    "Olive",
    "Robyn",
    "Robert",
    "Ryan",
    "Sarah",
    "Sean",
    "Teresa",
    "Tim",
    "Valerie",
    "Wayne",
    "William",
]


def create_sample_files(file_name: str, sample_size: int) -> None:
    """
    Create sample CSV and JSON files with random data.

    Args:
        file_name (str): The base name for the sample files (without extension).
        sample_size (int): The number of rows to generate for the sample files.

    Returns:
        None

    Raises:
        Exception: If an error occurs while creating the sample files.

    Example: ```python from dsg_lib import file_functions
    file_functions.create_sample_files("test", 100)  # Creates 'test.csv' and
    'test.json' each with 100 rows of random data ```
    """
    logger.debug(f"Creating sample files for {file_name} with {sample_size} rows.")

    try:
        # Generate the CSV data
        csv_header = ["name", "birth_date", "number"]
        csv_data: List[List[str]] = [csv_header]

        # Generate rows for CSV data
        for i in range(1, sample_size + 1):
            r_int: int = random.randint(0, len(first_name) - 1)
            name = first_name[r_int]
            row: List[str] = [name, generate_random_date(), str(i)]
            csv_data.append(row)

        # Save the CSV file
        csv_file = f"{file_name}.csv"
        save_csv(csv_file, csv_data)

        # Generate the JSON data
        json_data: List[dict] = []

        # Generate rows for JSON data
        for i in range(1, sample_size + 1):
            r_int: int = random.randint(0, len(first_name) - 1)
            name = first_name[r_int]
            sample_dict: dict = {
                "name": name,
                "birthday_date": generate_random_date(),
            }
            json_data.append(sample_dict)

        # Save the JSON file
        json_file: str = f"{file_name}.json"
        save_json(json_file, json_data)

        # Log the data
        logger.debug(f"CSV Data: {csv_data}")
        logger.debug(f"JSON Data: {json_data}")

    except Exception as e:  # pragma: no cover
        logger.exception(
            f"Error occurred while creating sample files: {e}"
        )  # pragma: no cover
        raise  # pragma: no cover


def generate_random_date() -> str:
    """
    Generate a random datetime string in the format yyyy-mm-dd hh:mm:ss.ffffff.

    Returns:
        str: A randomly generated datetime string.

    Example: ```python from dsg_lib import file_functions random_date =
    file_functions.generate_random_date()  # Returns: '1992-03-15
    10:30:45.123456' ```
    """
    # Define the minimum and maximum years for the date range
    min_year: int = 1905
    max_year: int = datetime.now().year

    # Generate random values for the year, month, day, hour, minute, and second
    year: int = random.randrange(min_year, max_year + 1)
    month: int = random.randint(1, 12)
    day: int = random.randint(1, 28)
    hour: int = random.randint(0, 12)
    minute: int = random.randint(0, 59)
    second: int = random.randint(0, 59)

    # Create a datetime object with the random values
    date_value: datetime = datetime(year, month, day, hour, minute, second)

    # Format the datetime string and return it
    return f"{date_value:%Y-%m-%d %H:%M:%S.%f}"


def save_text(file_name: str, data: str, root_folder: str = None) -> str:
    """
    Saves a string of text to a file with the specified file name in the
    specified directory.

    Args:
        file_name (str): The name of the file to save the data in. Should not
        include the '.txt' extension. data (str): The text data to be saved.
        root_folder (str, optional): The root directory where the file will be
        saved. If None, the file will be saved in the current directory.
        Defaults to None.

    Returns:
        str: A message indicating whether the file has been saved successfully
        or an error occurred.

    Raises:
        TypeError: If the `data` parameter is not a string, or the `file_name`
        contains a forward slash or backslash. FileNotFoundError: If the
        directory does not exist.

    Example: ```python from dsg_lib import file_functions
    file_functions.save_text("test", "This is a test text file.",
    "/path/to/directory")  # Saves data to '/path/to/directory/test.txt' ```
    """
    # If no root folder is provided, use the default directory
    if root_folder is None:  # pragma: no cover
        root_folder = directory_to_files  # pragma: no cover

    # Determine the directory for text files
    text_directory = Path(root_folder) / "text"

    # Construct the file path for text files
    file_path = text_directory / f"{file_name}.txt"

    # Create the text directory if it does not exist
    text_directory.mkdir(parents=True, exist_ok=True)

    # Check that data is a string and that file_name does not contain invalid
    # characters
    if not isinstance(data, str):
        logger.error(f"{file_name} is not a valid string")
        raise TypeError(f"{file_name} is not a valid string")
    elif "/" in file_name or "\\" in file_name:
        logger.error(f"{file_name} cannot contain \\ or /")
        raise ValueError(f"{file_name} cannot contain \\ or /")

    # Open or create the file and write the data
    with open(file_path, "w+", encoding="utf-8") as file:
        file.write(data)

    logger.info(f"File created: {file_path}")
    return "complete"


def open_text(file_name: str) -> str:
    """
    Opens a text file with the specified file name and returns its contents as a
    string.

    Args:
        file_name (str): The name of the file to open. Should include the '.txt'
        extension.

    Returns:
        str: The contents of the text file as a string.

    Raises:
        TypeError: If the `file_name` parameter is not a string or contains a
        forward slash. FileNotFoundError: If the file does not exist.

    Example: ```python from dsg_lib import file_functions data =
    file_functions.open_text("test.txt")  # Returns: 'This is a test text file.'
    ```
    """
    # Replace backslashes with forward slashes in the file name
    if "\\" in file_name:  # pragma: no cover
        file_name = file_name.replace("\\", "/")  # pragma: no cover

    # Check that file_name does not contain invalid characters
    if "/" in file_name:
        logger.error(f"{file_name} cannot contain /")
        raise TypeError(f"{file_name} cannot contain /")

    # Get the path to the text directory and the file path
    file_directory = os.path.join(directory_to_files, "text")
    file_path = Path.cwd().joinpath(file_directory, file_name)

    # Check if the file exists
    if not file_path.is_file():
        raise FileNotFoundError(f"file not found error: {file_path}")

    # Open the file and read the data
    with open(file_path, "r", encoding="utf-8") as file:
        data = file.read()

    logger.info(f"File opened: {file_path}")
    return data
