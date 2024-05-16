## Validating Email Addresses
Example of how to use in a script

```python

from dsg_lib.common_functions.email_validation import validate_email_address

import pprint
import time


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
        "test@google.com",
    ]

    # create a list of configurations
    configurations = [
        {"check_deliverability": True, "test_environment": False, "allow_smtputf8": False, "allow_empty_local": False, "allow_quoted_local": False, "allow_display_name": False, "allow_domain_literal": False, "globally_deliverable": None, "timeout": 10, "dns_type": 'timeout'},
        {"check_deliverability": False, "test_environment": True, "allow_smtputf8": True, "allow_empty_local": True, "allow_quoted_local": True, "allow_display_name": True, "allow_domain_literal": True, "globally_deliverable": None, "timeout": 5, "dns_type": 'dns'},
        {"check_deliverability": True},
        {"check_deliverability": False, "test_environment": False, "allow_smtputf8": True, "allow_empty_local": False, "allow_quoted_local": True, "allow_display_name": False, "allow_domain_literal": True, "globally_deliverable": None, "timeout": 15, "dns_type": 'timeout'},
        {"check_deliverability": True, "test_environment": True, "allow_smtputf8": False, "allow_empty_local": True, "allow_quoted_local": False, "allow_display_name": True, "allow_domain_literal": False, "globally_deliverable": None, "timeout": 20, "dns_type": 'dns'},
        {"check_deliverability": False, "test_environment": False, "allow_smtputf8": True, "allow_empty_local": True, "allow_quoted_local": True, "allow_display_name": True, "allow_domain_literal": True, "globally_deliverable": None, "timeout": 25, "dns_type": 'timeout'},
        {"check_deliverability": True, "test_environment": True, "allow_smtputf8": False, "allow_empty_local": False, "allow_quoted_local": False, "allow_display_name": False, "allow_domain_literal": False, "globally_deliverable": None, "timeout": 30, "dns_type": 'dns'},
        {"check_deliverability": False, "test_environment": True, "allow_smtputf8": True, "allow_empty_local": False, "allow_quoted_local": True, "allow_display_name": True, "allow_domain_literal": False, "globally_deliverable": None, "timeout": 35, "dns_type": 'timeout'},
        {"check_deliverability": True, "test_environment": False, "allow_smtputf8": False, "allow_empty_local": True, "allow_quoted_local": True, "allow_display_name": False, "allow_domain_literal": True, "globally_deliverable": None, "timeout": 40, "dns_type": 'dns'},
        {"check_deliverability": False, "test_environment": True, "allow_smtputf8": True, "allow_empty_local": False, "allow_quoted_local": False, "allow_display_name": True, "allow_domain_literal": True, "globally_deliverable": None, "timeout": 45, "dns_type": 'timeout'},
    ]

    t0 = time.time()
    validity=[]

    for email in email_addresses:
        for config in configurations:

            res = validate_email_address(email, **config)
            validity.append(res)
    t1 = time.time()
    validity = sorted(validity, key=lambda x: x['email'])

    for v in validity:
            pprint.pprint(v, indent=4)

    print(f"Time taken: {t1 - t0:.2f}")
```
