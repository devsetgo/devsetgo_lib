# -*- coding: utf-8 -*-
from enum import Enum
from typing import Dict, List, Union
from loguru import logger
from email_validator import (
    EmailNotValidError,
    EmailUndeliverableError,
    caching_resolver,
    validate_email,
)


class DNSType(Enum):
    DNS = "dns"
    TIMEOUT = "timeout"


def validate_email_address(
    email: str,
    check_deliverability: bool = True,
    test_environment: bool = False,
    allow_smtputf8: bool = False,
    allow_empty_local: bool = False,
    allow_quoted_local:bool=False,
    allow_display_name: bool = False,
    allow_domain_literal: bool = False,
    globally_deliverable: bool = None,
    timeout: int = 10,
    dns_type: str = 'timeout',
) -> Dict[str, Union[str, bool, Dict[str, Union[str, bool, List[str]]]]]:

    logger.debug(f"validate_email_address: {email} with params: {locals()}")
    valid: bool = False

    dns_type = dns_type.lower()

    if dns_type == 'dns':
        dns_resolver = caching_resolver(timeout=timeout)
        dns_param = {"dns_resolver": dns_resolver}
    elif dns_type == 'timeout':
        if timeout is None:
            timeout = 5
        dns_param = {"timeout": timeout}

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

        email: str = emailinfo.normalized

        email_dict: Dict[
            str, Union[str, bool, Dict[str, Union[str, bool, List[str]]]]
        ] = {
            "email": email,
            "valid": False,
            "email_data": None,
        }
        email_data: Dict[str, Union[str, bool, List[str]]] = {}

        if hasattr(emailinfo, "mx"):
            email_data["mx"] = emailinfo.mx
            if emailinfo.mx is not None:
                email_dict["valid"] = True
                logger.info(f"Email is valid: {email}")
            else:
                if emailinfo.normalized is not None:
                    email_dict["valid"] = True
                logger.info(F"Email no MX record found: {email}")

        email_dict["email_data"] = dict(sorted(vars(emailinfo).items()))

        return email_dict

    except EmailUndeliverableError as e:
        return {"valid": valid, "email": email, "error": str(e)}
    except EmailNotValidError as e:
        return {"valid": valid, "email": email, "error": str(e)}
    except Exception as e:
        return {"valid": valid, "email": email, "error": str(e)}


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
        "mike@google.com",
        # Emails with empty local part
        "@example.com",  # only valid if allow_empty_local is True

        # Emails with non-ASCII characters
        "üñîçøðé@example.com",  # only valid if allow_smtputf8 is True
        "user@üñîçøðé.com",  # only valid if allow_smtputf8 is True

        # Emails with quoted local part
        '"john.doe"@example.com',  # only valid if allow_quoted_local is True
        '"john..doe"@example.com',  # only valid if allow_quoted_local is True

        # Emails with display name
        'John Doe <john@example.com>',  # only valid if allow_display_name is True

        # Emails with domain literal
        'user@[192.0.2.1]',  # only valid if allow_domain_literal is True

        # Emails with long local part
        "a"*65 + "@example.com",  # local part is longer than 64 characters

        # Emails with invalid characters
        "john doe@example.com",  # space is not allowed
        "john@doe@example.com",  # only one @ is allowed
        "john.doe@.com",  # domain can't start with a dot
        "john.doe@example..com",  # domain can't have two consecutive dots
    ]
    # create a list of configurations
    configurations = [
        {"check_deliverability": True, "test_environment": False, "allow_smtputf8": False, "allow_empty_local": False, "allow_quoted_local": False, "allow_display_name": False, "allow_domain_literal": False, "globally_deliverable": None, "timeout": 10, "dns_type": 'timeout'},
        {"check_deliverability": False, "test_environment": True, "allow_smtputf8": True, "allow_empty_local": True, "allow_quoted_local": True, "allow_display_name": True, "allow_domain_literal": True, "globally_deliverable": None, "timeout": 5, "dns_type": 'dns'},
        # add more configurations here
    ]

    import pprint
    import time

    t0 = time.time()
    validity=[]
    for _ in range(20):
        for email in email_addresses:
            for config in configurations:

                res = validate_email_address(email, **config)
                # if res['valid']:
                #     pprint.pprint(res, indent=4)
                # pprint.pprint(res, indent=4)
                # print(f"Time taken: {time.time() - t0:.2f}")
                # print(f"Email: {email} is valid: {res['valid']}")
                # validity.append(f"Email: {email} is valid: {res['valid']}")
                validity.append(res)
    t1 = time.time()
    validity = sorted(validity, key=lambda x: x['email'])

    for v in validity:
         pprint.pprint(v, indent=4)

    print(f"Time taken: {t1 - t0:.2f}")
