# -*- coding: utf-8 -*-

"""
email_functions.py

This module contains a function for validating email addresses.
"""

# Import the time module to measure how long the email validation takes
import time

# Import the necessary functions and exceptions from the email_validator module
from email_validator import (
    EmailNotValidError,  # Exception raised when an email address is not valid
)
from email_validator import (
    EmailUndeliverableError,  # Exception raised when an email address is not deliverable
)
from email_validator import validate_email  # Function for validating email addresses

# Import the logger from the loguru module for logging
from loguru import logger


async def validate_email_address(
    email_address: str,
    check_deliverability: bool = True,
    test_environment: bool = False,
):
    """
    This function validates an email address.

    Parameters:
    email_address (str): The email address to validate.
    check_deliverability (bool): If True, checks whether the email address is deliverable.
    test_environment (bool): If True, runs the function in a test environment.

    Returns:
    dict: A dictionary containing information about the email address and any validation errors.
    """

    # Check if the email_address parameter is a string
    if isinstance(email_address, str) is False:
        raise ValueError("Email address must be a string")

    # Log the start of the email validation
    logger.debug(f"Validating email address: {email_address}")

    # Initialize a dictionary to store the validation results
    data = {
        "message": None,  # Will store any error messages
        "information": None,  # Will store information about the email address
        "dns_check": None,  # Will store a link to check the DNS records of the email domain
        "error": False,  # Will be set to True if there are any validation errors
        "timer": None,  # Will store the time taken to validate the email address
    }

    # Check if the email_address parameter is not empty
    if not email_address:
        data["message"] = "Email address is required"
        data["error"] = True
        logger.warning("Email address is required")
        return data

    # Extract the domain from the email address
    domain = email_address.split("@")[1]

    # Generate a link to check the DNS records of the email domain
    data[
        "dns_check"
    ] = f"https://dnschecker.org/all-dns-records-of-domain.php?query={domain}&rtype=ALL&dns=google"

    # Try to validate the email address using the validate_email function
    try:
        # The validate_email function returns a data object with information about the email address
        email_data = validate_email(
            email_address,
            check_deliverability=check_deliverability,
            test_environment=test_environment,
        )

        # Store the information from the email_data object in the data dictionary
        data["information"] = {
            "normalized": email_data.normalized,  # The normalized email address
            "valid": True,  # The email address is valid
            "local_part": email_data.local_part,  # The local part of the email address (before the @)
            "domain": email_data.domain,  # The domain of the email address (after the @)
            "ascii_email": email_data.ascii_email,  # The email address in ASCII format
            "ascii_local_part": email_data.ascii_local_part,  # The local part of the email address in ASCII format
            "ascii_domain": email_data.ascii_domain,  # The domain of the email address in ASCII format
            "smtputf8": email_data.smtputf8,  # Whether the email address uses SMTPUTF8 (allows Unicode in email addresses)
            "mx": None
            if not check_deliverability
            else email_data.mx,  # The MX record of the email domain, if check_deliverability is True
            "mx_fallback_type": None
            if not check_deliverability
            else email_data.mx_fallback_type,  # The type of MX record fallback used, if check_deliverability is True
        }

        # Set the message in the data dictionary to indicate that the email validation was successful
        data["message"] = "Email validation successful"

        # Log that the email validation was successful
        logger.info("Email validation successful")

        # Return the data dictionary
        return data

    # If the email address is not deliverable, catch the EmailUndeliverableError
    except EmailUndeliverableError as ex:
        # Set the message in the data dictionary to the error message
        data["message"] = f"EmailUndeliverableError '{str(ex)}'"

        # Set error in the data dictionary to True
        data["error"] = True

        # Log the error
        logger.error(f"EmailUndeliverableError '{str(ex)}'")

        # Return the data dictionary
        return data

    # If the email address is not valid, catch the EmailNotValidError
    except EmailNotValidError as ex:
        # Set the message in the data dictionary to the error message
        data["message"] = f"EmailNotValidError '{str(ex)}'"

        # Set error in the data dictionary to True
        data["error"] = True

        # Log the error
        logger.error(f"EmailNotValidError '{str(ex)}'")
    # If a general exception occurs, catch it
    except Exception as ex:
        # Set the message in the data dictionary to the error message
        data[
            "message"
        ] = f"An Exception '{str(ex)}' has occured. This could be due to no value is set on the domain."

        # Set error in the data dictionary to True
        data["error"] = True

        # Log the error as a critical issue
        logger.critical(
            f"An Exception '{str(ex)}' has occured. This could be due to no value is set on the domain."
        )

    # Return the data dictionary
    return data
