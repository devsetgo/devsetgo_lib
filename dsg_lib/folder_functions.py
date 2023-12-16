# -*- coding: utf-8 -*-
"""
This module contains functions for working with directories and files.

Functions:
    last_data_files_changed(directory_path): Get the last modified file in a
    directory and return its modification time and path.
    get_directory_list(file_directory): Get a list of directories in the
    specified directory. make_folder(file_directory): Make a folder in a
    specific directory. remove_folder(file_directory): Remove a folder from the
    specified directory.

Example: ```python from dsg_lib import folder_functions

# Get the last modified file in a directory time_stamp, file_path =
folder_functions.last_data_files_changed("/path/to/directory")  # Returns:
(datetime.datetime(2022, 1, 1, 12, 0, 0), '/path/to/directory/test.txt')

# Get a list of directories in the specified directory directories =
folder_functions.get_directory_list("/path/to/directory")  # Returns:
['/path/to/directory/dir1', '/path/to/directory/dir2']

# Make a folder in a specific directory
folder_functions.make_folder("/path/to/directory/new_folder")  # Creates a new
folder at '/path/to/directory/new_folder'

# Remove a folder from the specified directory
folder_functions.remove_folder("/path/to/directory/old_folder")  # Removes the
folder at '/path/to/directory/old_folder' ```
"""
import re
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

from loguru import logger

# Define the directory where the files are located
directory_to__files: str = "data"
file_directory = f"{directory_to__files}/csv"
directory_path = Path.cwd().joinpath(file_directory)


def last_data_files_changed(directory_path: str) -> Tuple[datetime, str]:
    """
    Get the last modified file in a directory and return its modification time
    and path.

    Args:
        directory_path (str): The path of the directory to check.

    Returns:
        Tuple[datetime, str]: A tuple containing the modification time and path
        of the last modified file.

    Raises:
        FileNotFoundError: If the directory does not exist.

    Example: ```python from dsg_lib import file_functions time_stamp, file_path
    = file_functions.last_data_files_changed("/path/to/directory")  # Returns:
    (datetime.datetime(2022, 1, 1, 12, 0, 0), '/path/to/directory/test.txt') ```
    """
    try:
        # Use a generator expression to find the last modified file in the
        # directory
        time, file_path = max((f.stat().st_mtime, f) for f in directory_path.iterdir())

        # Convert the modification time to a datetime object
        time_stamp = datetime.fromtimestamp(time)

        # Log a message to indicate that the directory was checked for the last
        # modified file
        logger.info(f"Directory checked for last change: {directory_path}")

        # Return the modification time and path of the last modified file
        return time_stamp, file_path

    except Exception as err:
        # Log an error message if an exception occurs, and return a default
        # value to indicate an error
        logger.error(err)
        return None, None


def get_directory_list(file_directory: str) -> List[str]:
    """
    Get a list of directories in the specified directory.

    Args:
        file_directory (str): The path of the directory to check.

    Returns:
        List[str]: A list of directories in the specified directory.

    Raises:
        FileNotFoundError: If the directory does not exist.

    Example: ```python from dsg_lib import file_functions directories =
    file_functions.get_directory_list("/path/to/directory")  # Returns:
    ['/path/to/directory/dir1', '/path/to/directory/dir2'] ```
    """
    # Create a Path object for the specified directory
    file_path = Path.cwd().joinpath(file_directory)

    try:
        # Use a list comprehension to create a list of directories in the
        # specified directory
        direct_list = [x for x in file_path.iterdir() if x.is_dir()]

        # Log a message indicating that the list of directories was retrieved
        logger.info(f"Retrieved list of directories: {file_directory}")

        # Return the list of directories
        return direct_list

    except FileNotFoundError as err:
        # Log an error message if the specified directory does not exist
        logger.error(err)


def make_folder(file_directory):
    def make_folder(file_directory: str) -> bool:
        """
        Make a folder in a specific directory.

        Args:
            file_directory (str): The directory in which to create the new
            folder.

        Returns:
            bool: True if the folder was created successfully, False otherwise.

        Raises:
            FileExistsError: If the folder already exists. ValueError: If the
            folder name contains invalid characters.

        Example: ```python from dsg_lib import file_functions
        file_functions.make_folder("/path/to/directory/new_folder")  # Creates a
        new folder at '/path/to/directory/new_folder' ```
        """

    # Check if the folder already exists
    if file_directory.is_dir():
        error = f"Folder exists: {file_directory}"
        logger.error(error)
        raise FileExistsError(error)

    # Check for invalid characters in folder name
    invalid_chars = re.findall(r'[<>:"/\\|?*]', file_directory.name)
    if invalid_chars:
        error = f"Invalid characters in directory name: {invalid_chars}"
        logger.error(error)
        raise ValueError(error)

    # Create the new folder
    Path.mkdir(file_directory)
    logger.info(f"Directory created: {file_directory}")

    return True


def remove_folder(file_directory: str) -> None:
    """
    Remove a folder from the specified directory.

    Args:
        file_directory (str): The directory containing the folder to be removed.

    Returns:
        None.

    Raises:
        FileNotFoundError: If the specified directory does not exist. OSError:
        If the specified folder could not be removed.

    Example: ```python from dsg_lib import file_functions
    file_functions.remove_folder("/path/to/directory/old_folder")  # Removes the
    folder at '/path/to/directory/old_folder' ```
    """
    try:
        # Create a Path object for the specified directory
        path = Path(file_directory)

        # Use the rmdir method of the Path object to remove the folder
        path.rmdir()

        # Log a message indicating that the folder was removed
        logger.info(f"Folder removed: {file_directory}")

    except FileNotFoundError as err:
        # Log an error message if the specified directory does not exist
        logger.error(err)

        # Raise the FileNotFoundError exception to be handled by the calling
        # code
        raise

    except OSError as err:
        # Log an error message if the folder could not be removed
        logger.error(err)

        # Raise the OSError exception to be handled by the calling code
        raise
