# -*- coding: utf-8 -*-
import logging
from datetime import datetime
from pathlib import Path
import re

log_format = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
logging.basicConfig(format=log_format, level=logging.INFO)

# Directory Path
directory_to__files: str = "data"
file_directory = f"{directory_to__files}/csv"  # /{directory}"
directory_path = Path.cwd().joinpath(file_directory)


def last_data_files_changed(directory_path):
    try:
        time, file_path = max((f.stat().st_mtime, f) for f in directory_path.iterdir())
        time_stamp = datetime.fromtimestamp(time)

        logging.info(f"directory checked for last change: {file_directory}")
        return time_stamp, file_path
    except Exception as e:
        logging.error(e)


def get_directory_list(file_directory):
    """getting a list of directories"""
    direct_list = []
    file_path = Path.cwd().joinpath(file_directory)
    try:
        # loop through directory
        for x in file_path.iterdir():
            # check if it is a directory
            if x.is_dir():
                # add to list
                direct_list.append(x)
        # return list of items in directory
        logging.info(f"getting a list of directories: {file_directory}")
        return direct_list

    except FileNotFoundError as e:
        logging.error(e)


def make_folder(file_directory):
    """
    Make a folder in a specific directory.

    Args:
        file_directory (pathlib.Path): The directory in which to create the new folder.

    Returns:
        bool: True if the folder was created successfully, False otherwise.

    Raises:
        FileExistsError: If the folder already exists.
        ValueError: If the folder name contains invalid characters.
    """

    # Check if the folder already exists
    if file_directory.is_dir():
        error = f"Folder exists: {file_directory}"
        logging.error(error)
        raise FileExistsError(error)

    # Check for invalid characters in folder name
    invalid_chars = re.findall(r'[<>:"/\\|?*]', file_directory.name)
    if invalid_chars:
        error = f"Invalid characters in directory name: {invalid_chars}"
        logging.error(error)
        raise ValueError(error)

    # Create the new folder
    Path.mkdir(file_directory)
    logging.info(f"Directory created: {file_directory}")

    return True


def remove_folder(file_directory):
    """making a folder in a specific directory"""
    try:
        Path.rmdir(file_directory)
        logging.info(f"direct removed: at {file_directory}")
    except OSError as e:
        logging.error(e)
