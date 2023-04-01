# -*- coding: utf-8 -*-
import logging
import re
from datetime import datetime
from pathlib import Path

log_format = {
    "asctime": "%(asctime)s [UTC%(asctime:z)]",
    "name": "%(name)s",
    "levelname": "%(levelname)s",
    "message": "%(message)s",
}

logging.basicConfig(format=log_format, level=logging.INFO)

# Directory Path
directory_to__files: str = "data"
file_directory = f"{directory_to__files}/csv"  # /{directory}"
directory_path = Path.cwd().joinpath(file_directory)


def last_data_files_changed(directory_path):
    """
    Get the last modified file in a directory and return its modification time and path.

    Args:
        directory_path (pathlib.Path): The directory to search for the last modified file.

    Returns:
        Tuple[datetime.datetime, pathlib.Path]: A tuple containing the modification time and path of the last modified file,
        or (None, None) if there was an error.

    """
    try:
        # Use a generator expression to find the last modified file in the directory
        time, file_path = max((f.stat().st_mtime, f) for f in directory_path.iterdir())

        # Convert the modification time to a datetime object
        time_stamp = datetime.fromtimestamp(time)

        # Log a message to indicate that the directory was checked for the last modified file
        logging.info(f"Directory checked for last change: {directory_path}")

        # Return the modification time and path of the last modified file
        return time_stamp, file_path

    except Exception as err:
        # Log an error message if an exception occurs, and return a default value to indicate an error
        logging.error(err)
        return None, None


def get_directory_list(file_directory):
    """Get a list of directories in the specified directory.

    Args:
        file_directory (str): The directory to search for directories.

    Returns:
        A list of directories in the specified directory.

    Raises:
        FileNotFoundError: If the specified directory does not exist.
    """
    # Create a Path object for the specified directory
    file_path = Path.cwd().joinpath(file_directory)

    try:
        # Use a list comprehension to create a list of directories in the specified directory
        direct_list = [x for x in file_path.iterdir() if x.is_dir()]

        # Log a message indicating that the list of directories was retrieved
        logging.info(f"Retrieved list of directories: {file_directory}")

        # Return the list of directories
        return direct_list

    except FileNotFoundError as err:
        # Log an error message if the specified directory does not exist
        logging.error(err)


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
    """Remove a folder from the specified directory.

    Args:
        file_directory (str): The directory containing the folder to be removed.

    Returns:
        None.

    Raises:
        FileNotFoundError: If the specified directory does not exist.
        OSError: If the specified folder could not be removed.
    """
    try:
        # Create a Path object for the specified directory
        path = Path(file_directory)

        # Use the rmdir method of the Path object to remove the folder
        path.rmdir()

        # Log a message indicating that the folder was removed
        logging.info(f"Folder removed: {file_directory}")

    except FileNotFoundError as err:
        # Log an error message if the specified directory does not exist
        logging.error(err)

        # Raise the FileNotFoundError exception to be handled by the calling code
        raise

    except OSError as err:
        # Log an error message if the folder could not be removed
        logging.error(err)

        # Raise the OSError exception to be handled by the calling code
        raise
