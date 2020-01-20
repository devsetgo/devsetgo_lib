# -*- coding: utf-8 -*-
from datetime import datetime
from pathlib import Path

# remove loguru and place your favorite logging mechanism
from loguru import logger

# Directory Path
directory_to__files: str = "data"
file_directory = f"{directory_to__files}/csv"  # /{directory}"
directory_path = Path.cwd().joinpath(file_directory)


def last_data_files_changed(directory_path):
    try:
        time, file_path = max((f.stat().st_mtime, f) for f in directory_path.iterdir())
        time_stamp = datetime.fromtimestamp(time)

        logger.info(f"directory checked for last change: {file_directory}")
        return time_stamp, file_path
    except Exception as e:
        logger.error(e)


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
        logger.info(f"getting a list of directories: {file_directory}")
        return direct_list

    except FileExistsError as e:
        logger.error(e)


# TODO: add check of BAD_CHARACTERS = [":", "*", "?", "|", "<", ">"]
def make_folder(file_directory):
    """ making a folder in a specific directory"""

    try:
        Path.mkdir(file_directory)
        logger.info(f"directory created: at {file_directory}")
    except FileExistsError as e:
        logger.error(e)


def remove_folder(file_directory):
    """ making a folder in a specific directory"""
    try:

        Path.rmdir(file_directory)
        logger.info(f"direct removed: at {file_directory}")
    except OSError as e:
        logger.error(e)
