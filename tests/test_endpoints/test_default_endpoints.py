# -*- coding: utf-8 -*-
from fastapi import FastAPI
from fastapi.testclient import TestClient

from dsg_lib.fastapi_functions.default_endpoints import create_default_router

# Create a FastAPI app for testing
app = FastAPI()
client = TestClient(app)

# User configuration for default endpoints
config = [
    {"bot": "Bytespider", "allow": False},
    {"bot": "GPTBot", "allow": False},
    {"bot": "ClaudeBot", "allow": True},
    {"bot": "ImagesiftBot", "allow": True},
    {"bot": "CCBot", "allow": False},
    {"bot": "ChatGPT-User", "allow": True},
    {"bot": "omgili", "allow": False},
    {"bot": "Diffbot", "allow": False},
    {"bot": "Claude-Web", "allow": True},
    {"bot": "PerplexityBot", "allow": False},
    {"bot": "Googlebot", "allow": True},
    {"bot": "Bingbot", "allow": True},
    {"bot": "Baiduspider", "allow": False},
    {"bot": "YandexBot", "allow": False},
    {"bot": "DuckDuckBot", "allow": True},
    {"bot": "Sogou", "allow": False},
    {"bot": "Exabot", "allow": False},
    {"bot": "facebot", "allow": False},
    {"bot": "ia_archiver", "allow": False},
]

# Default router
default_router = create_default_router(config)
app.include_router(default_router, prefix="", tags=["default"])


def test_robots_txt():
    response = client.get("/robots.txt")
    assert response.status_code == 200
    content = response.text
    assert "User-agent: Bytespider" in content
    assert "Disallow: /" in content
    assert "User-agent: GPTBot" in content
    assert "Disallow: /" in content
    assert "User-agent: ClaudeBot" in content
    assert "Allow: /" in content
    assert "User-agent: Googlebot" in content
    assert "Allow: /" in content
    assert "User-agent: Baiduspider" in content
    assert "Disallow: /" in content
