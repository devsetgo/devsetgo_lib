# -*- coding: utf-8 -*-
"""
TODO: Need  documentation here
"""
from typing import Optional

from packaging import version as packaging_version

# Try to import FastAPI, handle ImportError if FastAPI is not installed
try:
    from pydantic import BaseModel, EmailStr, Field
except ImportError:
    BaseModel = EmailStr = Field = None

# Check FastAPI version
min_version = "2.0"  # replace with your minimum required version
if pydantic is not None and packaging_version.parse(
    pydantic.__version__
) < packaging_version.parse(min_version):
    raise ImportError(
        f"Pydantic version >= {min_version} required, run `pip install --upgrade pydantic[email]`"
    )


class EmailVerification(BaseModel):
    """
    A Pydantic model representing an email verification request.

    Attributes:
        email_address (EmailStr): The email address to be checked. This field is required.
        check_deliverability (Optional[bool]): If True, the DNS of the domain will be checked to verify deliverability. Defaults to True.
        test_environment (Optional[bool]): If True, the DNS check will be bypassed. This is useful for test environments where the email server might not be reachable. Defaults to False.

    Example:
        email_verification = EmailVerification(
            email_address="test@gmail.com",
            check_deliverability=True,
            test_environment=False,
        )
    """

    email_address: EmailStr = Field(
        ...,
        description="The email address to be checked. Must be a valid email format.",
        examples=["test@gmail.com", "example@test.com"],
        max_length=255,
    )
    check_deliverability: Optional[bool] = Field(
        True,
        description="If True, the DNS of the domain will be checked to verify deliverability.",
    )
    test_environment: Optional[bool] = Field(
        False,
        description="If True, the DNS check will be bypassed. Useful for test environments where the email server might not be reachable.",
    )


class EmailValidationResponse(BaseModel):
    """
    A Pydantic model representing the response from the email validation endpoint.

    Attributes:
        message (str): A message indicating the result of the email validation.
        information (Optional[dict]): Information about the validated email. This could be None in case of an error.
        error (bool): Indicates if there was an error during the validation.
        timer (float): The time taken to perform the validation.
    """

    message: str = Field(
        ...,
        description="A message indicating the result of the email validation.",
        example="Email validation successful",
    )
    information: Optional[dict] = Field(
        None,
        description="Information about the validated email. This could be None in case of an error.",
        example={
            "normalized": "test@gmail.com",
            "valid": True,
            "local_part": "test",
            "domain": "gmail.com",
            "ascii_email": "test@gmail.com",
            "ascii_local_part": "test",
            "ascii_domain": "gmail.com",
            "smtputf8": False,
            "mx": [
                [5, "gmail-smtp-in.l.google.com"],
                [10, "alt1.gmail-smtp-in.l.google.com"],
            ],
            "mx_fallback_type": "None",
        },
    )
    error: bool = Field(
        ...,
        description="Indicates if there was an error during the validation.",
        example=False,
    )
    timer: float = Field(
        ..., description="The time taken to perform the validation.", example=0.3556
    )
    dns_check: str = Field(
        ...,
        description="The time taken to perform the validation.",
        example="https://dnschecker.org/all-dns-records-of-domain.php?query=gmail.com&rtype=ALL&dns=google",
    )
