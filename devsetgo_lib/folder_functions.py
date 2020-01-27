# -*- coding: utf-8 -*-
from datetime import datetime
from pathlib import Path
import logging

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
    """ getting a list of directories"""
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


# TODO: add check of BAD_CHARACTERS = [":", "*", "?", "|", "<", ">"]
def make_folder(file_directory):
    """ making a folder in a specific directory"""

    if file_directory.is_dir() is True:
        error = f"Folder exists: {file_directory}"
        logging.error(error)
        raise FileNotFoundError(error)

    Path.mkdir(file_directory)
    logging.info(f"directory created: at {file_directory}")


def remove_folder(file_directory):
    """ making a folder in a specific directory"""
    try:

        Path.rmdir(file_directory)
        logging.info(f"direct removed: at {file_directory}")
    except OSError as e:
        logging.error(e)
