# -*- coding: utf-8 -*-
"""
This module provides two main functions to convert between month numbers and
their corresponding names.

Functions:
    get_month(month: int) -> str:
        Converts an integer month number to its corresponding month name.

        Args:
            month (int): An integer between 1 and 12 representing the month
            number.

        Returns:
            str: The full name of the month corresponding to the input month
            number.
                 If the input is not within the range of 1-12, returns "Invalid
                 month number". If the input is not an integer, returns "Invalid
                 input, integer is required".

    get_month_number(month_name: str) -> int:
        Converts a month name to its corresponding month number.

        Args:
            month_name (str): A string containing the full name of a month.

        Returns:
            int: The month number corresponding to the input month name.
                 If the input is not a valid month name, returns -1. If the
                 input is not a string, returns "Invalid input, string is
                 required".

Example:
```python
from dsg_lib.common_functions.calendar_functions import get_month,

get_month_number print(get_month(1))

# Outputs: 'January'

print(get_month_number('January'))

# Outputs: 1
```

This module is part of the dsg_lib package and is used for handling and
converting between month numbers and names.

Author: Mike Ryan
Date: 2024/05/16
License: MIT
"""
# from loguru import logger
# import logging as logger
from .. import LOGGER as logger

# Names of all months, indexed by (month number - 1). Module-level so it's
# built once instead of on every get_month() call.
MONTHS = (
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
)

# Reverse lookup of MONTHS, built once instead of on every
# get_month_number() call.
MONTH_NUMBERS = {name: number for number, name in enumerate(MONTHS, start=1)}


def get_month(month: int) -> str:
    """
    Converts an integer month number to its corresponding month name.

    Args:
        month (int): An integer or integer-like float between 1 and 12
        representing the month number.

    Returns:
        str: The full name of the month corresponding to the input month number.
             If the input is not within the range of 1-12, returns "Invalid
             month number". If the input is not an integer or integer-like
             float, returns "Invalid input, integer is required".
    """
    # Convert integer-like floats to integers
    if isinstance(month, float) and month.is_integer():
        month = int(month)

    # Check if the input month is an integer
    if not isinstance(month, int):
        logger.error("Invalid input: %s, integer is required", month)
        return "Invalid input, integer is required"

    # Check if the input month is within the range of 1-12
    if 1 <= month <= 12:
        logger.info("Returning month name for month number: %s", month)
        return MONTHS[month - 1]
    else:
        logger.error(
            "Invalid input: %s, month number should be between 1 and 12", month
        )
        return "Invalid month number"


def get_month_number(month_name: str) -> int:
    """
    Converts a month name to its corresponding month number.

    Args:
        month_name (str): A string containing the full name of a month.

    Returns:
        int: The month number corresponding to the input month name.
             If the input is not a valid month name or not a string, returns -1.
    """

    # Check if the input month name is a string
    if not isinstance(month_name, str):
        logger.error("Invalid input, string is required")
        return -1

    # Convert the input string to title case and remove leading/trailing spaces
    month_name = month_name.strip().title()

    # Check if the input month name is a valid key in the lookup
    if month_name in MONTH_NUMBERS:
        return MONTH_NUMBERS[month_name]
    else:
        logger.error("Invalid month name: %s", month_name)
        return -1
