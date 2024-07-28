# -*- coding: utf-8 -*-
"""
This module provides functionality for validating email addresses.

The main function in this module is `validate_email_address`, which takes an email address and a set of optional parameters to control the validation process. It uses the `email_validator` library to perform the validation and returns a dictionary containing the validation result and other information about the email address.

The module also defines a `DNSType` enum for specifying the type of DNS resolver to use during the validation process.

The `validate_email_address` function supports the following optional parameters:
- `check_deliverability`: If True, the function checks whether the email address is deliverable.
- `test_environment`: If True, the function operates in test mode and does not actually send any emails.
- `allow_smtputf8`: If True, the function allows non-ASCII characters in the email address.
- `allow_empty_local`: If True, the function allows email addresses with an empty local part.
- `allow_quoted_local`: If True, the function allows email addresses with a quoted local part.
- `allow_display_name`: If True, the function allows email addresses with a display name.
- `allow_domain_literal`: If True, the function allows email addresses with a domain literal.
- `globally_deliverable`: If True, the function checks whether the email address is globally deliverable.
- `timeout`: The timeout for the DNS resolver, in seconds.
- `dns_type`: The type of DNS resolver to use, either 'dns' or 'timeout'.

Example:
    To use the `validate_email` function in this module, you can do the following:

    ```python
    from email_validation import validate_email

    email = "test@example.com"
    if validate_email(email):
        print(f"{email} is valid.")
    else:
        print(f"{email} is not valid.")
    ```
See example for more use or bottom of module for more use examples.

Author: Mike Ryan
Date: 2024/05/16
License: MIT
"""
from enum import Enum
from typing import Dict, List, Union

from email_validator import (
    EmailNotValidError,
    EmailUndeliverableError,
    caching_resolver,
    validate_email,
)
from loguru import logger


class DNSType(Enum):
    """
    Enum representing the type of DNS resolver to use during email validation.

    This enum is used in the `validate_email_address` function to specify the type of DNS resolver to use when checking the deliverability of an email address. The `DNS` option uses a standard DNS resolver, while the `TIMEOUT` option uses a DNS resolver with a specified timeout.

    Attributes:
        DNS (str): Represents a standard DNS resolver.
        TIMEOUT (str): Represents a DNS resolver with a specified timeout.
    """

    DNS = "dns"
    TIMEOUT = "timeout"


def validate_email_address(
    email: str,
    check_deliverability: bool = True,
    test_environment: bool = False,
    allow_smtputf8: bool = False,
    allow_empty_local: bool = False,
    allow_quoted_local: bool = False,
    allow_display_name: bool = False,
    allow_domain_literal: bool = False,
    globally_deliverable: bool = None,
    timeout: int = 10,
    dns_type: str = "dns",
) -> Dict[str, Union[str, bool, Dict[str, Union[str, bool, List[str]]]]]:
    """
    Validates an email address and returns a dictionary with the validation result and other information.

    This function uses the `email_validator` library to validate the email address. It supports a variety of optional parameters to control the validation process, such as whether to check deliverability, whether to allow non-ASCII characters, and the type of DNS resolver to use.

    Args:
        email (str): The email address to validate.
        check_deliverability (bool, optional): If True, checks whether the email address is deliverable. Defaults to True.
        test_environment (bool, optional): If True, operates in test mode and does not actually send any emails. Defaults to False.
        allow_smtputf8 (bool, optional): If True, allows non-ASCII characters in the email address. Defaults to False.
        allow_empty_local (bool, optional): If True, allows email addresses with an empty local part. Defaults to False.
        allow_quoted_local (bool, optional): If True, allows email addresses with a quoted local part. Defaults to False.
        allow_display_name (bool, optional): If True, allows email addresses with a display name. Defaults to False.
        allow_domain_literal (bool, optional): If True, allows email addresses with a domain literal. Defaults to False.
        globally_deliverable (bool, optional): If True, checks whether the email address is globally deliverable. Defaults to None.
        timeout (int, optional): The timeout for the DNS resolver, in seconds. Defaults to 10.
        dns_type (str, optional): The type of DNS resolver to use, either 'dns' or 'timeout'. Defaults to 'dns'.

    Returns:
        Dict[str, Union[str, bool, Dict[str, Union[str, bool, List[str]]]]]: A dictionary containing the validation result and other information about the email address.

    Raises:
        ValueError: If `dns_type` is not 'dns' or 'timeout'.
        EmailUndeliverableError: If the email address is not deliverable.
        EmailNotValidError: If the email address is not valid according to the `email_validator` library.
        Exception: If any other error occurs during the validation process.
    """
    # Log the function call with the provided parameters
    logger.debug(f"validate_email_address: {email} with params: {locals()}")

    # Initialize the valid flag to False
    valid: bool = False

    # Convert the dns_type to a DNSType enum
    try:
        dns_type = DNSType(dns_type.lower())
    except ValueError:
        raise ValueError(
            "dns_type must be either 'dns' or 'timeout'. Default is 'dns' if not provided or input is None."
        )

    # Set up the DNS resolver based on the dns_type
    if dns_type == DNSType.DNS:
        dns_resolver = caching_resolver(timeout=timeout)
        dns_param = {"dns_resolver": dns_resolver}
    elif dns_type == DNSType.TIMEOUT:
        if timeout is None or timeout <= 0 or isinstance(timeout, int) is False:
            timeout = 5
        dns_param = {"timeout": timeout}

    # Validate the email address
    try:
        emailinfo = validate_email(
            email,
            check_deliverability=check_deliverability,
            test_environment=test_environment,
            allow_smtputf8=allow_smtputf8,
            allow_empty_local=allow_empty_local,
            allow_domain_literal=allow_domain_literal,
            globally_deliverable=globally_deliverable,
            **dns_param,
        )

        # Normalize the email address
        email: str = emailinfo.normalized

        # Initialize the return dictionary
        email_dict: Dict[
            str, Union[str, bool, Dict[str, Union[str, bool, List[str]]]]
        ] = {
            "email": email,
            "valid": valid,
            "email_data": None,
        }

        # Check the deliverability of the email address
        if not check_deliverability or emailinfo.mx is not None:
            email_dict["valid"] = True
            logger.info(f"Email is valid: {email}")
        else:  # pragma: no cover
            email_dict["valid"] = False
            logger.info(f"Email invalid: {email}")

        # Add the email info and parameters to the return dictionary
        email_dict["email_data"] = dict(sorted(vars(emailinfo).items()))
        email_dict["parameters"] = dict(sorted(locals().items()))

        # return the dictionary
        return email_dict

    # Handle EmailUndeliverableError
    except EmailUndeliverableError as e:
        error = str(e)
        parameters = dict(sorted(locals().items()))
        email_dict = {
            "valid": False,
            "email": email,
            "error": error,
            "error_type": "EmailUndeliverableError",
            "parameters": parameters,
        }
        logger.error(f"EmailUndeliverableError: {email} - {str(e)}")
        logger.debug(f"EmailUndeliverableError: {email} - {str(e)}, - {parameters}")
        return email_dict

    # Handle EmailNotValidError
    except EmailNotValidError as e:
        error = str(e)
        parameters = dict(sorted(locals().items()))
        email_dict = {
            "valid": False,
            "email": email,
            "error": error,
            "error_type": "EmailNotValidError",
            "parameters": parameters,
        }
        logger.error(f"EmailNotValidError: {email} - {str(e)}")
        logger.debug(f"EmailNotValidError: {email} - {str(e)}, - {parameters}")
        return email_dict

    # Handle other exceptions
    except Exception as e:  # pragma: no cover
        error = str(e)
        parameters = dict(sorted(locals().items()))
        email_dict = {
            "valid": False,
            "email": email,
            "error": error,
            "error_type": "Exception",
            "parameters": parameters,
        }
        logger.error(f"Exception: {email} - {str(e)}")
        logger.debug(f"Exception: {email} - {str(e)}, - {parameters}")
        return email_dict


if __name__ == "__main__":
    # create a list of email addresses to check if valid
    email_addresses = [
        "bob@devsetgo.com",
        "bob@devset.go",
        "foo@yahoo.com",
        "bob@gmail.com",
        "very fake@devsetgo.com",
        "jane.doe@example.com",
        "john_doe@example.co.uk",
        "user.name+tag+sorting@example.com",
        "x@example.com",  # shortest possible email address
        "example-indeed@strange-example.com",
        "admin@mailserver1",  # local domain name with no TLD
        "example@s.example",  # see the list of Internet top-level domains
        '" "@example.org',  # space between the quotes
        '"john..doe"@example.org',  # quoted double dot
        "mailhost!username@example.org",  # bangified host route used for uucp mailers
        "user%example.com@example.org",  # percent sign in local part
        "user-@example.org",  # valid due to the last character being an allowed character
        # Invalid email addresses
        "Abc.example.com",  # no @ character
        "A@b@c@example.com",  # only one @ is allowed outside quotation marks
        'a"b(c)d,e:f;g<h>i[j\\k]l@example.com',  # none of the special characters in this local part are allowed outside quotation marks
        'just"not"right@example.com',  # quoted strings must be dot separated or the only element making up the local-part
        'this is"not\\allowed@example.com',  # spaces, quotes, and backslashes may only exist when within quoted strings and preceded by a backslash
        'this\\ still\\"not\\\\allowed@example.com',  # even if escaped (preceded by a backslash), spaces, quotes, and backslashes must still be contained by quotes
        "1234567890123456789012345678901234567890123456789012345678901234+x@example.com",  # local part is longer than 64 characters
        # Emails with empty local part
        "@example.com",  # only valid if allow_empty_local is True
        # Emails with non-ASCII characters
        "üñîçøðé@example.com",  # only valid if allow_smtputf8 is True
        "user@üñîçøðé.com",  # only valid if allow_smtputf8 is True
        # Emails with quoted local part
        '"john.doe"@example.com',  # only valid if allow_quoted_local is True
        '"john..doe"@example.com',  # only valid if allow_quoted_local is True
        # Emails with display name
        "John Doe <john@example.com>",  # only valid if allow_display_name is True
        # Emails with domain literal
        "user@[192.0.2.1]",  # only valid if allow_domain_literal is True
        # Emails with long local part
        "a" * 65 + "@example.com",  # local part is longer than 64 characters
        # Emails with invalid characters
        "john doe@example.com",  # space is not allowed
        "john@doe@example.com",  # only one @ is allowed
        "john.doe@.com",  # domain can't start with a dot
        "john.doe@example..com",  # domain can't have two consecutive dots
        "test@google.com",
    ]

    # create a list of configurations
    configurations = [
        {
            "check_deliverability": True,
            "test_environment": False,
            "allow_smtputf8": False,
            "allow_empty_local": False,
            "allow_quoted_local": False,
            "allow_display_name": False,
            "allow_domain_literal": False,
            "globally_deliverable": None,
            "timeout": 10,
            "dns_type": "timeout",
        },
        {
            "check_deliverability": False,
            "test_environment": True,
            "allow_smtputf8": True,
            "allow_empty_local": True,
            "allow_quoted_local": True,
            "allow_display_name": True,
            "allow_domain_literal": True,
            "globally_deliverable": None,
            "timeout": 5,
            "dns_type": "dns",
        },
        {"check_deliverability": True},
        # add more configurations here
    ]

    import pprint
    import time

    t0 = time.time()
    validity = []

    for email in email_addresses:
        for config in configurations:

            res = validate_email_address(email, **config)
            validity.append(res)
    t1 = time.time()
    validity = sorted(validity, key=lambda x: x["email"])

    for v in validity:
        pprint.pprint(v, indent=4)

    print(f"Time taken: {t1 - t0:.2f}")
