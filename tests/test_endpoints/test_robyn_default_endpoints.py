# -*- coding: utf-8 -*-
from robyn import Robyn
from robyn.testing import TestClient as RobynTestClient

from dsg_lib.robyn_functions.default_endpoints import create_default_router

config = [
    {"bot": "Bytespider", "allow": False},
    {"bot": "GPTBot", "allow": False},
    {"bot": "ClaudeBot", "allow": True},
    {"bot": "Googlebot", "allow": True},
]


def make_client(**kwargs):
    app = Robyn(__file__)
    app.include_router(create_default_router(config, **kwargs))
    return RobynTestClient(app)


def test_robots_txt():
    response = make_client().get("/robots.txt")
    assert response.status_code == 200
    assert response.headers.get("Content-Type") == "text/plain"
    assert response.text == (
        "User-agent: *\n"
        "User-agent: Bytespider\n"
        "Disallow: /\n"
        "User-agent: GPTBot\n"
        "Disallow: /\n"
        "User-agent: ClaudeBot\n"
        "Allow: /\n"
        "User-agent: Googlebot\n"
        "Allow: /"
    )


def test_robots_txt_with_prefix():
    client = make_client(prefix="/static")
    assert client.get("/static/robots.txt").status_code == 200
    assert client.get("/robots.txt").status_code == 404
