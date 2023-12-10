# -*- coding: utf-8 -*-
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from dsg_lib.fastapi_endpoints.models import EmailVerification
from dsg_lib.fastapi_endpoints.system_tools_endpoints import create_tool_router

# Create a FastAPI app for testing
app = FastAPI()
client = TestClient(app)
# Tools configuration
route_name = "/api"
config_tools = {"enable_email-validation": True}
tool_router = create_tool_router(config=config_tools)
app.include_router(tool_router, prefix=route_name, tags=["system-tools"])


def test_create_tool_router():
    config = {"enable_email-validation": True}
    router = create_tool_router(config)
    assert router is not None


@patch("dsg_lib.fastapi_endpoints.system_tools_endpoints.validate_email_address")
def test_check_email(mock_validate_email_address):
    # Set up the mock function to return a valid response
    mock_validate_email_address.return_value = {
        "message": "Email validation successful",
        "information": {
            "normalized": "test@gmail.com",
            "valid": True,
            "local_part": "test",
            "domain": "gmail.com",
            "ascii_email": "test@gmail.com",
            "ascii_local_part": "test",
            "ascii_domain": "gmail.com",
            "smtputf8": False,
            "mx": None,
            "mx_fallback_type": None,
        },
        "dns_check": "https://dnschecker.org/all-dns-records-of-domain.php?query=gmail.com&rtype=ALL&dns=google",
        "error": False,
        "timer": None,
    }

    email_verification = EmailVerification(
        email_address="test@gmail.com",
        check_deliverability=True,
        test_environment=False,
    )
    response = client.post(
        f"{route_name}/email-validation", json=email_verification.dict()
    )
    if response.status_code != 200:
        print(response.text)
    assert response.status_code == 200
    assert "valid" in response.json()["information"]
