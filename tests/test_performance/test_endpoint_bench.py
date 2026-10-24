# -*- coding: utf-8 -*-
"""
Tests for speedtest/endpoint_bench.py. The comparison and rendering tests are
pure functions and run in the normal suite. The `perf`-marked smoke test
starts a real FastAPI server and is deselected by default; run it with
`pytest -m perf` (or `make perf-smoke`).
"""
import importlib.util
import json
import sys

import pytest

from speedtest import endpoint_bench as bench

PROFILE = {"platform": "Linux x86_64", "cpu_count": 8, "python": "3.14.0", "clients": 4, "concurrency": 50}


def record(status_rps, status_p99, **overrides):
    rec = {
        "version": "2026.1.1.1",
        "git_sha": "abc1234",
        "date": "2026-01-01",
        **PROFILE,
        "requests": 100,
        "frameworks": {
            "fastapi": {
                bench.KEY_ENDPOINT: {"rps": status_rps, "p50_ms": 1, "p95_ms": 2, "p99_ms": status_p99, "errors": 0}
            }
        },
        "logging_us": {"loguru_info_defaults": 12.5},
    }
    rec.update(overrides)
    return rec


def test_compare_flags_rps_drop_and_p99_rise():
    problems = bench.compare(record(1000, 10), record(700, 20))
    assert len(problems) == 2
    assert "rps fell" in problems[0] and "p99 rose" in problems[1]


def test_compare_within_limits_is_clean():
    assert bench.compare(record(1000, 10), record(900, 12)) == []


def test_compare_ignores_other_machine_profiles():
    other = record(1000, 10, cpu_count=64)
    assert bench.compare(other, record(10, 999)) == []
    assert bench.compare(None, record(10, 999)) == []


def test_compare_skips_framework_missing_from_previous():
    previous = record(1000, 10)
    current = record(1000, 10)
    current["frameworks"]["robyn"] = {bench.KEY_ENDPOINT: {"rps": 1, "p99_ms": 1}}
    assert bench.compare(previous, current) == []


def test_previous_on_same_profile_picks_latest_match():
    a, b, c = record(1, 1), record(2, 2, cpu_count=2), record(3, 3)
    assert bench.previous_on_same_profile([a, b, c], record(0, 0)) is c
    assert bench.previous_on_same_profile([b], record(0, 0)) is None


def test_summarize_percentiles():
    result = bench.summarize([float(i) for i in range(1, 101)], errors=1, requests=100, elapsed=2.0)
    assert result == {"rps": 50.0, "p50_ms": 50.5, "p95_ms": 95.0, "p99_ms": 99.0, "errors": 1}
    assert bench.summarize([], 0, 1, 1.0)["p99_ms"] == 0.0


def test_render_page_empty_and_with_history():
    assert "No runs recorded yet" in bench.render_page([])
    page = bench.render_page([record(1000, 10), record(1200, 9, version="2026.1.2.1")])
    assert "## Latest run" in page and "## History" in page
    assert "`2026.1.2.1`" in page and "1,200" in page
    assert "| n/a | n/a |" in page  # robyn missing from these records
    # Newest first in the history table.
    assert page.index("`2026.1.2.1`", page.index("## History")) < page.index("`2026.1.1.1`", page.index("## History"))


def test_main_regression_exit_codes(tmp_path, monkeypatch):
    history = tmp_path / "history.json"
    history.write_text(json.dumps([record(1000, 10)]))
    slow = {"fastapi": {bench.KEY_ENDPOINT: {"rps": 100, "p50_ms": 1, "p95_ms": 1, "p99_ms": 100, "errors": 0}}}
    monkeypatch.setattr(bench, "framework_commands", lambda: {"fastapi": ["unused"]})
    monkeypatch.setattr(bench, "bench_framework", lambda *a: slow["fastapi"])
    monkeypatch.setattr(bench, "machine_profile", lambda: {k: PROFILE[k] for k in ("platform", "cpu_count", "python")})
    args = ["--history", str(history), "--page", str(tmp_path / "index.md"), "--log-messages", "0",
            "--clients", "4", "--concurrency", "50"]
    assert bench.main(args + ["--no-write"]) == 2
    assert bench.main(args + ["--no-write", "--no-fail"]) == 0
    assert len(json.loads(history.read_text())) == 1
    assert bench.main(args + ["--no-fail"]) == 0
    assert len(json.loads(history.read_text())) == 2
    assert (tmp_path / "index.md").exists()


def _smoke(tmp_path, framework):
    history = tmp_path / "history.json"
    page = tmp_path / "index.md"
    code = bench.main(
        [
            "--frameworks", framework,
            "--requests", "40",
            "--concurrency", "4",
            "--warmup", "4",
            "--clients", "2",
            "--log-messages", "200",
            "--history", str(history),
            "--page", str(page),
            "--no-fail",
        ]
    )
    assert code == 0
    rec = json.loads(history.read_text())[-1]
    assert set(rec["frameworks"][framework]) == set(bench.ENDPOINTS)
    assert all(r["errors"] == 0 for r in rec["frameworks"][framework].values())
    assert rec["logging_us"]["loguru_info_defaults"] > 0
    assert "## Latest run" in page.read_text()


@pytest.mark.perf
def test_endpoint_bench_smoke(tmp_path):
    _smoke(tmp_path, "fastapi")


@pytest.mark.perf
@pytest.mark.skipif(importlib.util.find_spec("robyn") is None, reason="Robyn not installed")
def test_endpoint_bench_smoke_robyn(tmp_path):
    _smoke(tmp_path, "robyn")


def test_server_start_failure_includes_stderr():
    # A server that dies at once must report why, not just its exit code.
    argv = [sys.executable, "-c", "import sys; sys.stderr.write('boom: bad config'); sys.exit(3)"]
    with pytest.raises(RuntimeError) as excinfo:
        bench.bench_framework("broken", argv, requests=1, concurrency=1, warmup=1, clients=1)
    message = str(excinfo.value)
    assert "broken: server exited early with code 3" in message
    assert "boom: bad config" in message


def test_stderr_tail_handles_missing_and_empty(tmp_path):
    assert bench._stderr_tail(tmp_path / "missing") == ""
    empty = tmp_path / "empty"
    empty.write_text("")
    assert bench._stderr_tail(empty) == ""
