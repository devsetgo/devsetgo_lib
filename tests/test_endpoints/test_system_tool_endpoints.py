# -*- coding: utf-8 -*-
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from dsg_lib.endpoints.models import EmailVerification
from dsg_lib.endpoints.system_tools_endpoints import create_tool_router

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


def test_check_email():
    email_verification = EmailVerification(
        email_address="test@gmail.com",
        check_deliverability=True,
        test_environment=False,
    )
    response = client.post(
        f"{route_name}/email-validation", json=email_verification.model_dump()
    )
    if response.status_code != 200:
        print(response.text)
    assert response.status_code == 200
    assert "valid" in response.json()
