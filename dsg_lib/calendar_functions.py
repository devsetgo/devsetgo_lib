# -*- coding: utf-8 -*-
import logging

log_format = {
    "asctime": "%(asctime)s [UTC%(asctime:z)]",
    "name": "%(name)s",
    "levelname": "%(levelname)s",
    "message": "%(message)s",
}

logging.basicConfig(format=log_format, level=logging.INFO)


def get_month(month: int) -> str:
    """
    Takes an integer month number and returns the corresponding month name as a string.

    Args:
        month (int): An integer between 1 and 12 representing the month number.

    Returns:
        str: The full name of the month corresponding to the input month number.
             If the input is not within the range of 1-12, returns "Invalid month number".
    """

    # Define a tuple containing the names of all months
    months = (
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

    # Convert float inputs to integers
    if isinstance(month, float) and float(month).is_integer():
        month = int(month)

    # Check if the input month is within the range of 1-12
    if isinstance(month, int) == False:
        # If the input month is not an integer, log an error message and return an error message
        logging.error("Invalid input: %s, integer is required", month)
        return "Invalid input, integer is required"
    elif 1 <= month <= 12:
        # Return the month name corresponding to the input month number
        logging.info("Returning month name for month number: %s", month)
        return months[month - 1]
    else:
        # If the input month is outside the range of 1-12, log an error message and return an error message
        logging.error(
            "Invalid input: %s, month number should be between 1 and 12", month
        )
        return "Invalid month number"


def get_month_number(month_name: str) -> int:
    """
    Takes a month name as a string and returns the corresponding month number as an integer.

    Args:
        month_name (str): A string containing the full name of a month.

    Returns:
        int: The month number corresponding to the input month name.
             If the input is not a valid month name, returns -1.
    """

    # Define a dictionary mapping month names to month numbers
    month_dict = {
        "January": 1,
        "February": 2,
        "March": 3,
        "April": 4,
        "May": 5,
        "June": 6,
        "July": 7,
        "August": 8,
        "September": 9,
        "October": 10,
        "November": 11,
        "December": 12,
    }

    # Set up logging
    logger = logging.getLogger(__name__)

    # Check if the input month name is a string
    if isinstance(month_name, str) == False:
        # If the input month is not a string, log an error and return -1
        logger.error("Invalid input, string is required")
        return -1

    # Convert the input string to title case and remove leading/trailing spaces
    month_name = month_name.strip().title()

    # Check if the input month name is a valid key in the dictionary
    if month_name in month_dict:
        # Return the month number corresponding to the input month name
        return month_dict[month_name]
    else:
        # If the input month name is not valid, log an error and return -1
        logger.error("Invalid month name: %s", month_name)
        return -1
