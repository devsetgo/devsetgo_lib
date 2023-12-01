# -*- coding: utf-8 -*-
"""
TODO: Need  documentation here
"""
from pydantic import BaseModel, Field


class EmailVerification(BaseModel):
    email_address: str = Field(
        ...,
        description="The email address to be checked",
        examples=["test@gmail.com"],
    )
    check_deliverability: bool = Field(True, description="Check the dns of the domain")
    test_environment: bool = Field(
        False, description="Used for test environments to bypass dns check"
    )
