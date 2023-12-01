# -*- coding: utf-8 -*-

from devsetgo_toolkit import ALL_HTTP_CODES, generate_code_dict


def test_generate_code_dict_description_only():
    codes = [200, 404]
    result = generate_code_dict(codes, description_only=True)
    assert result == {200: "OK", 404: "Not Found"}


def test_generate_code_dict_all_info():
    codes = [200, 404]
    result = generate_code_dict(codes, description_only=False)
    assert result == {200: ALL_HTTP_CODES[200], 404: ALL_HTTP_CODES[404]}


def test_generate_code_dict_invalid_code():
    codes = [999]
    result = generate_code_dict(codes, description_only=True)
    assert result == {}


def test_generate_code_dict_empty_codes():
    codes = []
    result = generate_code_dict(codes, description_only=True)
    assert result == {}
