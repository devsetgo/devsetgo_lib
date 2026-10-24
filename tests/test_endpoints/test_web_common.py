# -*- coding: utf-8 -*-
import tracemalloc
from unittest.mock import patch

import pytest

from dsg_lib.fastapi_functions import http_codes as fastapi_http_codes
from dsg_lib.robyn_functions import http_codes as robyn_http_codes
from dsg_lib.web_common import http_codes
from dsg_lib.web_common.health import (
    calculate_uptime,
    get_heap_dump,
    start_tracemalloc_for_heapdump,
)
from dsg_lib.web_common.robots import build_robots_txt


def test_build_robots_txt_empty_config():
    assert build_robots_txt([]) == "User-agent: *"


def test_build_robots_txt_allow_and_disallow():
    content = build_robots_txt(
        [{"bot": "GPTBot", "allow": False}, {"bot": "Googlebot", "allow": True}]
    )
    assert content == (
        "User-agent: *\n"
        "User-agent: GPTBot\n"
        "Disallow: /\n"
        "User-agent: Googlebot\n"
        "Allow: /"
    )


def test_build_robots_txt_defaults_allow_and_skips_missing_bot():
    content = build_robots_txt([{"bot": "Bingbot"}, {"allow": False}])
    assert content == "User-agent: *\nUser-agent: Bingbot\nAllow: /"


def test_calculate_uptime():
    # 1 day, 2 hours, 3 minutes, 4.567 seconds after start
    elapsed = 86400 + 2 * 3600 + 3 * 60 + 4.567
    with patch("dsg_lib.web_common.health.time.time", return_value=1000 + elapsed):
        result = calculate_uptime(1000)
    assert result == {"uptime": {"Days": 1, "Hours": 2, "Minutes": 3, "Seconds": 4.57}}


def test_get_heap_dump():
    tracemalloc.start()
    try:
        result = get_heap_dump(limit=3)
    finally:
        tracemalloc.stop()
    assert set(result) == {"memory_use", "heap_dump"}
    assert set(result["memory_use"]) == {"current", "peak"}
    assert len(result["heap_dump"]) <= 3
    for item in result["heap_dump"]:
        assert set(item) == {"filename", "lineno", "size", "count"}


def test_get_heap_dump_raises_when_not_tracing():
    if tracemalloc.is_tracing():
        tracemalloc.stop()
    with pytest.raises(RuntimeError):
        get_heap_dump()


def test_http_codes_reexports_share_the_same_objects():
    # The fastapi_functions and robyn_functions modules are shims over
    # web_common, so the old import path keeps working with identical data.
    for module in (fastapi_http_codes, robyn_http_codes):
        assert module.ALL_HTTP_CODES is http_codes.ALL_HTTP_CODES
        assert module.generate_code_dict is http_codes.generate_code_dict
        assert module.GET_CODES is http_codes.GET_CODES


@pytest.mark.parametrize(
    "config",
    [
        {},
        {"enable_heapdump_endpoint": False},
        {"enable_heapdump_endpoint": True, "start_tracemalloc": False},
    ],
)
def test_start_tracemalloc_for_heapdump_does_not_start(config):
    with patch("dsg_lib.web_common.health.tracemalloc") as mock_tm:
        assert start_tracemalloc_for_heapdump(config) is False
    mock_tm.start.assert_not_called()


def test_start_tracemalloc_for_heapdump_starts_when_enabled():
    with patch("dsg_lib.web_common.health.tracemalloc") as mock_tm:
        mock_tm.is_tracing.return_value = False
        assert start_tracemalloc_for_heapdump({"enable_heapdump_endpoint": True}) is True
    mock_tm.start.assert_called_once_with()


def test_start_tracemalloc_for_heapdump_keeps_existing_tracing():
    # A host that already started tracing (possibly with more frames) must
    # not be reset to tracemalloc's default of 1 frame.
    with patch("dsg_lib.web_common.health.tracemalloc") as mock_tm:
        mock_tm.is_tracing.return_value = True
        assert start_tracemalloc_for_heapdump({"enable_heapdump_endpoint": True}) is False
    mock_tm.start.assert_not_called()
