# -*- coding: utf-8 -*-
from typing import Dict, List, Union

from email_validator import (
    EmailNotValidError,
    EmailUndeliverableError,
    caching_resolver,
    validate_email,
)
from loguru import logger


def validate_email_address(
    email: str,
    test_environment: bool = False,
    allow_smtputf8: bool = True,
    allow_empty_local: bool = True,
    allow_domain_literal: bool = True,
    globally_deliverable: bool = True,
    # timeout: int = 5,
) -> Dict[str, Union[str, bool, Dict[str, Union[str, bool, List[str]]]]]:
    # Log the email being validated
    logger.info(f'Validating email: {email}')
    valid: bool = False

    resolver = caching_resolver(timeout=5)
    try:
        # Validate the email address, checking for deliverability
        emailinfo = validate_email(
            email,
            check_deliverability=True,
            dns_resolver=resolver,
            test_environment=False,
            allow_smtputf8=True,
            allow_empty_local=True,
            allow_domain_literal=True,
            globally_deliverable=True,
            # timeout=5,
        )
        # Normalize the email address
        email: str = emailinfo.normalized

        # Initialize an empty dictionary to store email information
        email_dict: Dict[str, Union[str, bool, Dict[str, Union[str, bool, List[str]]]]] = {
            'email': email,
            'valid': False,
            'email_data': None,
        }
        email_data: Dict[str, Union[str, bool, List[str]]] = {}
        # Populate the dictionary with attributes from the validated email,
        # if they exist
        if hasattr(emailinfo, 'normalized'):
            email_data['normalized'] = emailinfo.normalized
        if hasattr(emailinfo, 'local_part'):
            email_data['local'] = emailinfo.local_part
        if hasattr(emailinfo, 'domain'):
            email_data['domain'] = emailinfo.domain
        if hasattr(emailinfo, 'ascii_email'):
            email_data['ascii_email'] = emailinfo.ascii_email
        if hasattr(emailinfo, 'ascii_local_part'):
            email_data['ascii_local'] = emailinfo.ascii_local_part
        if hasattr(emailinfo, 'ascii_domain'):
            email_data['ascii_domain'] = emailinfo.ascii_domain
        if hasattr(emailinfo, 'smtputf8'):
            email_data['smtputf8'] = emailinfo.smtputf8
        if hasattr(emailinfo, 'domain_address'):
            email_data['domain_address'] = emailinfo.domain_address
        if hasattr(emailinfo, 'display_name'):
            email_data['display_name'] = emailinfo.display_name
        if hasattr(emailinfo, 'mx'):
            email_data['mx'] = emailinfo.mx
            if emailinfo.mx is not None:
                email_dict['valid'] = True
                logger.info(f'Email is valid: {email}')
        if hasattr(emailinfo, 'mx_fallback_type'):
            email_data['mx_fallback_type'] = emailinfo.mx_fallback_type
        if hasattr(emailinfo, 'spf'):
            email_data['spf'] = emailinfo.spf

        # Log that the email is valid
        logger.info(f'Email is valid: {email}')
        # Return a dictionary indicating that the email is valid, along with
        # the normalized email and the email information dictionary
        email_dict['email_data'] = dict(sorted(email_data.items()))
        return email_dict

    except EmailUndeliverableError as e:
        # Log the error if email deliverability fails
        logger.error(f'Email deliverability failed for {email}: {str(e)}')
        # Return a dictionary indicating that the email is not deliverable,
        # along with the original email and the error message
        return {'valid': valid, 'email': email, 'error': str(e)}
    except EmailNotValidError as e:
        # Log the error if email validation fails
        logger.error(f'Email validation failed for {email}: {str(e)}')
        # Return a dictionary indicating that the email is not valid, along
        # with the original email and the error message
        return {'valid': valid, 'email': email, 'error': str(e)}
    except Exception as e:
        # Log the error if an unexpected exception occurs
        logger.error(f'An unexpected error occurred: {str(e)}')
        # Return a dictionary indicating that an unexpected error occurred,
        # along with the original email and the error message
        return {'valid': valid, 'email': email, 'error': str(e)}


if __name__ == '__main__':
    # create a list of email addresses to check if valid
    email_addresses = [
        'bob@devsetgo.com',
        'bob@devset.go',
        'foo@yahoo.com',
        'bob@gmail.com',
        'very fake@devsetgo.com',
        'jane.doe@example.com',
        'john_doe@example.co.uk',
        'user.name+tag+sorting@example.com',
        'x@example.com',  # shortest possible email address
        'example-indeed@strange-example.com',
        'admin@mailserver1',  # local domain name with no TLD
        'example@s.example',  # see the list of Internet top-level domains
        '" "@example.org',  # space between the quotes
        '"john..doe"@example.org',  # quoted double dot
        'mailhost!username@example.org',  # bangified host route used for uucp mailers
        'user%example.com@example.org',  # percent sign in local part
        'user-@example.org',  # valid due to the last character being an allowed character
        # Invalid email addresses
        'Abc.example.com',  # no @ character
        'A@b@c@example.com',  # only one @ is allowed outside quotation marks
        'a"b(c)d,e:f;g<h>i[j\\k]l@example.com',  # none of the special characters in this local part are allowed outside quotation marks
        'just"not"right@example.com',  # quoted strings must be dot separated or the only element making up the local-part
        'this is"not\\allowed@example.com',  # spaces, quotes, and backslashes may only exist when within quoted strings and preceded by a backslash
        'this\\ still\\"not\\\\allowed@example.com',  # even if escaped (preceded by a backslash), spaces, quotes, and backslashes must still be contained by quotes
        '1234567890123456789012345678901234567890123456789012345678901234+x@example.com',  # local part is longer than 64 characters
        '@micrsoft.com',
    ]

    import pprint
    import time

    for email in email_addresses:
        t0 = time.time()
        res = validate_email_address(email)

        pprint.pprint(res, indent=4)
        print(f'Time taken: {time.time() - t0:.2f}')
