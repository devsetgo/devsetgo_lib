# -*- coding: utf-8 -*-

# Import required modules
import csv  # For reading and writing CSV files
import json  # For reading and writing JSON files
import logging  # For logging messages to the console
import os  # For interacting with the operating system
import random  # For generating random values
from datetime import datetime  # For working with dates and times
from pathlib import Path  # For working with file paths
from typing import List  # For specifying the type of variables
import os
import json
import logging
from pathlib import Path


# Define the log format to be used by the logging module
log_format = {
    "asctime": "%(asctime)s [UTC%(asctime:z)]",
    "name": "%(name)s",
    "levelname": "%(levelname)s",
    "message": "%(message)s",
}

# Configure the logging module with the desired log format and log level
logging.basicConfig(format=log_format, level=logging.INFO)


# Set the path to the directory where the files are located
directory_to_files: str = "data"

# A dictionary that maps file types to directories
directory_map = {".csv": "csv", ".json": "json", ".txt": "text"}


def delete_file(file_name: str) -> str:
    """
    Delete a file with the specified file name.

    Args:
        file_name (str): The name of the file to be deleted.

    Returns:
        str: A string indicating that the file has been deleted.

    Raises:
        TypeError: If the file name is not a string.
        ValueError: If the file name contains a forward slash or backslash,
            or if the file type is not supported.
        FileNotFoundError: If the file does not exist.
    """
    logging.info(f"Deleting file: {file_name}")

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
    logging.info(f"File {file_name}{file_ext} deleted from file path: {file_path}")

    # Return a string indicating that the file has been deleted
    return "complete"


# Set the path to the directory where the files are located
directory_to_files: str = "data"

# A dictionary that maps file types to directories
directory_map = {".csv": "csv", ".json": "json", ".txt": "text"}


def save_json(file_name: str, data, root_folder: str = "data") -> str:
    """
    Saves a JSON file with the given file name and data.

    Args:
        file_name (str): The name of the file to save.
        data (list or dict): The data to write to the file.
        root_folder (str, optional): The root directory for the file. Defaults to "data".

    Returns:
        str: A string indicating that the file has been created.

    Raises:
        TypeError: If the data is not a list or a dictionary.
        ValueError: If the file name contains a forward slash or backslash.
    """
    try:
        # Validate inputs
        if not isinstance(data, (list, dict)):
            raise TypeError(
                f"data must be a list or a dictionary instead of type {type(data)}"
            )
        if "/" in file_name or "\\" in file_name:
            raise ValueError(f"{file_name} cannot contain \\ or /")

        # Construct file paths
        file_directory = os.path.join(root_folder, directory_map[".json"])
        file_save = Path(file_directory) / file_name

        # Create directory if it doesn't exist
        os.makedirs(file_directory, exist_ok=True)

        # Write data to file
        with open(file_save, "w+") as write_file:
            json.dump(data, write_file)

        # Log success message
        logging.info(f"File created: {file_save}")

        return "complete"

    except (TypeError, ValueError) as e:
        logging.error(f"Error creating file {file_name}: {e}")
        raise


# TODO: figure out a method of appending an existing json file


# Json Open file
def open_json(file_name: str):
    # check if file name is a string
    if isinstance(file_name, str) is False:
        error = f"{file_name} is not a valid string"
        logging.error(error)
        raise TypeError(error)

    file_directory = f"{directory_to__files}/json"
    # create file in filepath
    file_save = Path.cwd().joinpath(file_directory).joinpath(file_name)

    # Check if path correct
    if not os.path.isfile(file_save):
        error = f"file not found error: {file_save}"
        logging.error(error)
        raise FileNotFoundError(error)

    # open file
    with open(file_save) as read_file:
        # load file into data variable
        result: dict = json.load(read_file)

    logging.info(f"File Opened: {file_name}")
    return result


# CSV File Processing
# TODO: Append CSV
# CSV Save new file
def save_csv(
    file_name: str,
    data: list,
    root_folder: str = None,
    delimiter: str = None,
    quotechar: str = None,
):
    # set root if none
    if root_folder is None:
        root_folder = "data"

    # check delimiter option
    if delimiter is None:
        delimiter = ","
    elif len(delimiter) > 1:
        error = f"{delimiter} can only be a single character"
        logging.error(error)
        raise TypeError(error)

    # check quotechar option
    if quotechar is None:
        quotechar = '"'
    elif len(quotechar) > 1:
        error = f"{quotechar} can only be a single character"
        logging.error(error)
        raise TypeError(error)

    # check that data is a list
    if isinstance(data, list) is False:
        error = f"{data} is not a valid string"
        logging.error(error)
        raise TypeError(error)
    elif "/" in file_name or "\\" in file_name:
        error = f"{file_name} cannot contain \\ or /"
        logging.error(error)
        raise TypeError(error)

    if not os.path.exists(f"{root_folder}/csv"):
        os.makedirs(f"{root_folder}/csv")

    # add extension to file name
    file_name = f"{file_name}"
    file_directory = f"{directory_to__files}/csv"
    # create file in filepath
    file_save = Path.cwd().joinpath(file_directory).joinpath(file_name)

    # open/create file
    with open(file_save, "w+", encoding="utf-8", newline="") as write_file:
        # write data to file
        file_writer = csv.writer(
            write_file,
            delimiter=delimiter,
            quotechar=quotechar,
        )
        for row in data:
            file_writer.writerow(row)

    logging.info(f"File Create: {file_name}")
    return "complete"


# CSV Open file
# pass file name and optional delimiter (default is ',')
# Output is dictionary/json
# expectation is for file to be quote minimal and skipping initial spaces is
# a good thing
# modify as needed
def open_csv(
    file_name: str,
    delimit: str = None,
    quote_level: str = None,
    skip_initial_space: bool = True,
) -> list:
    quote_level_list: list = ["none", "minimal", "all"]
    # TODO: figure out how non-numeric is supposed to work
    # Python documentation as needed https://docs.python.org/3/library/csv.html

    if quote_level is None:
        quoting = csv.QUOTE_MINIMAL

    elif quote_level.lower() not in quote_level_list:
        error = f"quote_level '{quote_level}' is not valid type - {quote_level_list}"
        logging.error(error)
        raise ValueError(error)

    elif quote_level.lower() in quote_level_list:
        if quote_level.lower() == "none":
            quoting = csv.QUOTE_NONE

        # elif quote_level.lower() == "non-numeric":
        #     quoting = csv.QUOTE_NONNUMERIC

        elif quote_level.lower() == "minimal":
            quoting = csv.QUOTE_MINIMAL

        elif quote_level.lower() == "all":
            quoting = csv.QUOTE_ALL

        else:  # pragma: no cover
            error = f"quote_level '{quote_level}' has caused an unhandled, undefined, or unknown error"  # pragma: no cover
            logging.error(error)  # pragma: no cover
            raise ValueError(error)  # pragma: no cover

    # set delimiter if none
    if delimit is None:
        delimit = ","

    # check if file name is a string
    if isinstance(file_name, str) is False:
        error = f"{file_name} is not a valid string"
        logging.error(error)
        raise TypeError(error)

    # add extension to file name
    file_name: str = f"{file_name}"
    file_directory: str = f"{directory_to__files}/csv"
    # create file in filepath
    file_save = Path.cwd().joinpath(file_directory).joinpath(file_name)

    if not os.path.isfile(file_save):
        error = f"file not found error: {file_save}"
        logging.error(error)
        raise FileNotFoundError(error)

    # Try/Except block
    # open file
    data = []
    with open(file_save) as read_file:
        # load file into data variable
        csv_data = csv.DictReader(
            read_file,
            delimiter=delimit,
            quoting=quoting,
            skipinitialspace=skip_initial_space,
        )

        # convert list to JSON object
        title = csv_data.fieldnames
        # iterate through each row to create dictionary/json object
        for row in csv_data:
            data.extend([{title[i]: row[title[i]] for i in range(len(title))}])

        logging.info(f"File Opened: {file_name}")
    return data


# create sample csv file
def create_sample_files(file_name: str, sample_size: int):
    first_name: list = [
        "Daniel",
        "Catherine",
        "Valerie",
        "Michael",
        "Kristina",
        "Linda",
        "Olive",
        "Mollie",
        "Nadia",
        "Elisha",
        "Lorraine",
        "Nedra",
        "Voncile",
        "Katrina",
        "Alan",
        "Clementine",
        "Kanesha",
    ]

    csv_data = []
    count = 0
    for _ in range(sample_size):
        r_int: int = random.randint(0, len(first_name) - 1)
        if count == 0:
            sample_list: List[str] = ["name", "birth_date", "number"]
        else:
            sample_list: List[str] = [
                first_name[r_int],
                str(__gen_datetime()),
                count,
            ]  # type: ignore

        count += 1
        csv_data.append(sample_list)
        logging.info(sample_list)

    print(csv_data)
    csv_file = f"{file_name}.csv"
    save_csv(csv_file, csv_data)

    json_data = []
    for _ in range(sample_size):
        r_int = random.randint(0, len(first_name) - 1)
        sample_dict: dict = {
            "name": first_name[r_int],
            "birthday_date": str(__gen_datetime()),
        }
        json_data.append(sample_dict)
    json_file = f"{file_name}.json"
    save_json(json_file, json_data)


def __gen_datetime(min_year: int = None, max_year: int = None):
    if min_year is None:
        min_year = 1905
    if max_year is None:
        max_year = datetime.now().year
    # generate a datetime in format yyyy-mm-dd hh:mm:ss.000000
    year: int = random.randint(min_year, max_year)
    month: int = random.randint(1, 12)
    day: int = random.randint(1, 28)
    hour: int = random.randint(0, 12)
    minute: int = random.randint(0, 59)
    second: int = random.randint(0, 59)
    date_value: datetime = datetime(year, month, day, hour, minute, second)

    # print(date_value)
    return date_value


# Text File Processing
# Tex Save new file
def save_text(file_name: str, data: str, root_folder: str = None) -> str:
    """
    Save text to file. Input is the name of the file (x.txt, x.html, etc..)
    and the data to be written to file.

    Arguments:
        file_name {str} -- [description]
        data {str} -- [description]

    Returns:
        str -- [description]
    """
    # set root if none
    if root_folder is None:
        root_folder = "data"

    if not os.path.exists(f"{root_folder}/text"):
        os.makedirs(f"{root_folder}/text")

    # add extension to file name
    file_name = f"{file_name}"
    file_directory = f"{directory_to__files}/text"
    # create file in filepath
    file_save = Path.cwd().joinpath(file_directory).joinpath(file_name)

    if isinstance(data, str) is not True:
        error = f"{file_name} is not a valid string"
        logging.error(error)
        raise TypeError(f"{file_name} is not a valid string")

    elif "/" in file_name or "\\" in file_name:
        error = f"{file_name} cannot contain \\ or /"
        logging.error(error)
        raise TypeError(error)

    # open/create file
    f = open(file_save, "w+", encoding="utf-8")
    # write data to file
    f.write(data)
    f.close()
    logging.info(f"File Create: {file_name}")
    return "complete"


def open_text(file_name: str) -> str:
    """
    Open text file and return as string

    Arguments:
        file_name {str} -- [description]

    Returns:
        str -- [description]
    """
    # check if file name is a string
    if isinstance(file_name, str) is False:
        error = f"{file_name} is not a valid string"
        logging.error(error)
        raise TypeError(error)
    elif "/" in file_name or "\\" in file_name:
        error = f"{file_name} cannot contain \\ or /"
        logging.error(error)
        raise TypeError(error)

    # add extension to file name
    file_name: str = f"{file_name}"
    file_directory: str = f"{directory_to__files}/text"
    # create file in filepath
    file_save = Path.cwd().joinpath(file_directory).joinpath(file_name)
    if not os.path.isfile(file_save):
        raise FileNotFoundError(f"file not found error: {file_save}")

    # open/create file
    f = open(file_save, "r", encoding="utf-8")
    # write data to file
    data = f.read()

    logging.info(f"File Create: {file_name}")
    return data
