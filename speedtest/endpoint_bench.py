# -*- coding: utf-8 -*-
"""
Endpoint performance benchmark for dsg_lib's FastAPI and Robyn helpers.

Starts a minimal app per framework (speedtest/apps/), drives each endpoint
with a fixed number of concurrent requests, runs the logging micro-benchmark,
appends the results to docs/performance/history.json and regenerates
docs/performance/index.md from that history.

    python speedtest/endpoint_bench.py                 # full run, updates the docs
    python speedtest/endpoint_bench.py --no-fail       # never exit non-zero (used by `make bump`)
    python speedtest/endpoint_bench.py --requests 200 --concurrency 10 --no-write

Exit codes: 0 ok, 2 regression against the previous run on the same machine
profile (unless --no-fail). docs/performance/index.md is generated; edit this
script, not the page.
"""
import argparse
import asyncio
import datetime as dt
import importlib.util
import json
import os
import platform
import shutil
import socket
import statistics
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APPS = Path(__file__).resolve().parent / "apps"
HISTORY = ROOT / "docs" / "performance" / "history.json"
PAGE = ROOT / "docs" / "performance" / "index.md"

ENDPOINTS = ["/api/health/status", "/api/health/uptime", "/robots.txt", "/codes", "/log"]
KEY_ENDPOINT = "/api/health/status"
RPS_DROP_LIMIT = 0.20
P99_RISE_LIMIT = 0.25

sys.path.insert(0, str(ROOT))


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def framework_commands():
    """Return {framework: argv} for every framework installed here."""
    commands = {"fastapi": [sys.executable, str(APPS / "fastapi_app.py")]}
    if importlib.util.find_spec("robyn") is not None:
        commands["robyn"] = [
            sys.executable,
            str(APPS / "robyn_app.py"),
            "--processes",
            "1",
            "--workers",
            "1",
        ]
    return commands


def _percentile(sorted_values, pct):
    if not sorted_values:
        return 0.0
    # Nearest-rank percentile, clamped to the list bounds.
    index = min(len(sorted_values) - 1, max(0, round(pct / 100 * len(sorted_values)) - 1))
    return sorted_values[index]


async def _drive(base_url, path, requests, concurrency):
    """Send `requests` GETs with `concurrency` in flight; return (latencies_ms, errors)."""
    import httpx

    latencies, errors = [], 0
    remaining = requests
    limits = httpx.Limits(max_connections=concurrency, max_keepalive_connections=concurrency)
    async with httpx.AsyncClient(base_url=base_url, limits=limits, timeout=30) as client:

        async def worker():
            nonlocal errors, remaining
            # No lock needed: workers share one event loop and nothing awaits
            # between the check and the decrement. Keep it that way.
            while remaining > 0:
                remaining -= 1
                t0 = time.perf_counter()
                try:
                    response = await client.get(path)
                    if response.status_code != 200:
                        errors += 1
                except httpx.HTTPError:
                    errors += 1
                latencies.append((time.perf_counter() - t0) * 1000)

        await asyncio.gather(*(worker() for _ in range(concurrency)))
    return latencies, errors


def _client_process(args):
    """Entry point for one load-generator process."""
    return asyncio.run(_drive(*args))


def summarize(latencies, errors, requests, elapsed):
    latencies = sorted(latencies)
    return {
        "rps": round(requests / elapsed, 1),
        "p50_ms": round(statistics.median(latencies), 2) if latencies else 0.0,
        "p95_ms": round(_percentile(latencies, 95), 2),
        "p99_ms": round(_percentile(latencies, 99), 2),
        "errors": errors,
    }


def load(pool, clients, base_url, path, requests, concurrency):
    """
    Split the load across `clients` processes. One Python process running
    httpx tops out well below what the servers can handle, so a single
    client would measure the client instead of the server.
    """
    per_client = max(1, requests // clients)
    per_conc = max(1, concurrency // clients)
    jobs = [(base_url, path, per_client, per_conc)] * clients
    started = time.perf_counter()
    results = list(pool.map(_client_process, jobs))
    elapsed = time.perf_counter() - started
    latencies = [lat for lats, _ in results for lat in lats]
    errors = sum(err for _, err in results)
    return summarize(latencies, errors, per_client * clients, elapsed)


def _stderr_tail(stderr_path, lines=20):
    try:
        text = Path(stderr_path).read_text(errors="replace")
    except OSError:
        return ""
    tail = "\n".join(text.splitlines()[-lines:])
    return f"\n--- server stderr (last {lines} lines) ---\n{tail}" if tail else ""


def _wait_ready(base_url, proc, timeout=30.0):
    import httpx

    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            raise RuntimeError(f"server exited early with code {proc.returncode}")
        try:
            if httpx.get(base_url + KEY_ENDPOINT, timeout=1).status_code == 200:
                return
        except httpx.HTTPError:
            pass
        time.sleep(0.2)
    raise RuntimeError(f"server at {base_url} did not become ready in {timeout}s")


def bench_framework(name, argv, requests, concurrency, warmup, clients):
    from concurrent.futures import ProcessPoolExecutor

    port = _free_port()
    workdir = tempfile.mkdtemp(prefix=f"dsg_bench_{name}_")
    env = {**os.environ, "DSG_BENCH_PORT": str(port), "DSG_BENCH_LOG_DIR": "log"}
    stderr_path = Path(workdir) / "server.stderr"
    stderr_file = open(stderr_path, "w")
    proc = subprocess.Popen(
        argv, cwd=workdir, env=env, stdout=subprocess.DEVNULL, stderr=stderr_file
    )
    base_url = f"http://127.0.0.1:{port}"
    try:
        try:
            _wait_ready(base_url, proc)
        except RuntimeError as ex:
            # Without the server's own output, a failed start gives no reason.
            raise RuntimeError(f"{name}: {ex}{_stderr_tail(stderr_path)}") from ex
        results = {}
        with ProcessPoolExecutor(clients) as pool:
            for path in ENDPOINTS:
                load(pool, clients, base_url, path, max(warmup, clients), concurrency)
                results[path] = load(pool, clients, base_url, path, requests, concurrency)
                print(f"  {name:8s} {path:22s} {results[path]}")
        return results
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:  # pragma: no cover
            proc.kill()
        stderr_file.close()
        shutil.rmtree(workdir, ignore_errors=True)


def machine_profile():
    return {
        "platform": f"{platform.system()} {platform.machine()}",
        "cpu_count": os.cpu_count(),
        "python": platform.python_version(),
    }


def _git_sha():
    """Short commit hash, with "-dirty" if dsg_lib/ has uncommitted changes."""
    try:
        sha = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        dirty = subprocess.run(
            ["git", "status", "--porcelain", "--", "dsg_lib"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"
    return f"{sha}-dirty" if dirty else sha


def same_profile(a, b):
    # Load shape changes the numbers as much as hardware does, so runs with
    # different client counts or concurrency are not comparable.
    keys = ("platform", "cpu_count", "python", "clients", "concurrency")
    return all(a.get(k) == b.get(k) for k in keys)


def compare(previous, current, rps_drop=RPS_DROP_LIMIT, p99_rise=P99_RISE_LIMIT):
    """
    Compare the key endpoint between two runs on the same machine profile.

    Returns a list of human-readable regression messages (empty if none, or
    if the runs come from different machine profiles and can't be compared).
    """
    if previous is None or not same_profile(previous, current):
        return []
    problems = []
    for framework, endpoints in current["frameworks"].items():
        before = previous.get("frameworks", {}).get(framework, {}).get(KEY_ENDPOINT)
        after = endpoints.get(KEY_ENDPOINT)
        if not before or not after:
            continue
        if after["rps"] < before["rps"] * (1 - rps_drop):
            problems.append(
                f"{framework} {KEY_ENDPOINT}: rps fell from {before['rps']} to {after['rps']}"
            )
        if after["p99_ms"] > before["p99_ms"] * (1 + p99_rise):
            problems.append(
                f"{framework} {KEY_ENDPOINT}: p99 rose from {before['p99_ms']} ms to {after['p99_ms']} ms"
            )
    return problems


def load_history(path=HISTORY):
    if not Path(path).exists():
        return []
    return json.loads(Path(path).read_text())


def previous_on_same_profile(history, current):
    for record in reversed(history):
        if same_profile(record, current):
            return record
    return None


def _fmt_row(cells):
    return "| " + " | ".join(str(c) for c in cells) + " |"


def render_page(history):
    """Build docs/performance/index.md from the history records."""
    lines = [
        "# Performance",
        "",
        "<!-- Generated by speedtest/endpoint_bench.py from history.json. Do not edit by hand. -->",
        "",
        "Every release records how much this library costs a host application.",
        "`make perf` starts a minimal FastAPI app and a minimal Robyn app that mount",
        "only this library's routers, with `config_log()` writing to a file at INFO",
        "as a real host would. Each endpoint gets a fixed number of concurrent requests.",
        "The run also records the per-message cost of logging through `config_log()`.",
        "",
        "Numbers depend on the machine. Compare rows only when the platform, CPU count",
        "and Python version match. `make bump` runs this after every version bump.",
        "",
    ]
    if not history:
        lines.append("No runs recorded yet. Run `make perf`.")
        return "\n".join(lines) + "\n"

    latest = history[-1]
    lines += [
        "## Latest run",
        "",
        f"Version `{latest['version']}` at commit `{latest['git_sha']}` on {latest['date']}.",
        f"Machine: {latest['platform']}, {latest['cpu_count']} CPUs, Python {latest['python']}.",
        f"Load: {latest['requests']} requests per endpoint, {latest['concurrency']} in flight, "
        f"from {latest.get('clients', 1)} client processes.",
        "",
        _fmt_row(["Framework", "Endpoint", "Requests/s", "p50 ms", "p95 ms", "p99 ms", "Errors"]),
        _fmt_row(["---"] * 2 + ["---:"] * 5),
    ]
    for framework, endpoints in latest["frameworks"].items():
        for path, r in endpoints.items():
            lines.append(
                _fmt_row(
                    [framework, f"`{path}`", f"{r['rps']:,.0f}", r["p50_ms"], r["p95_ms"], r["p99_ms"], r["errors"]]
                )
            )
    if latest.get("logging_us"):
        lines += [
            "",
            "Logging cost per message (microseconds, lower is better):",
            "",
            _fmt_row(["Benchmark", "µs/msg"]),
            _fmt_row(["---", "---:"]),
        ]
        for label, us in latest["logging_us"].items():
            lines.append(_fmt_row([f"`{label}`", f"{us:.2f}"]))

    lines += [
        "",
        "## History",
        "",
        f"Requests per second and p99 latency for `{KEY_ENDPOINT}`, plus the logging cost with `config_log()` defaults.",
        "",
        _fmt_row(
            ["Version", "Commit", "Date", "Machine", "FastAPI rps", "FastAPI p99 ms", "Robyn rps", "Robyn p99 ms", "Log µs/msg"]
        ),
        _fmt_row(["---"] * 4 + ["---:"] * 5),
    ]
    for record in reversed(history):
        cells = [f"`{record['version']}`", f"`{record['git_sha']}`", record["date"], f"{record['platform']} / {record['cpu_count']} CPU / py{record['python']}"]
        for framework in ("fastapi", "robyn"):
            r = record["frameworks"].get(framework, {}).get(KEY_ENDPOINT)
            cells += [f"{r['rps']:,.0f}", r["p99_ms"]] if r else ["n/a", "n/a"]
        log_us = (record.get("logging_us") or {}).get("loguru_info_defaults")
        cells.append(f"{log_us:.2f}" if log_us is not None else "n/a")
        lines.append(_fmt_row(cells))
    return "\n".join(lines) + "\n"


def run_logging_bench(messages):
    from speedtest.logging_bench import run

    return {k: round(v, 2) for k, v in run(messages).items()}


def main(argv=None):
    parser = argparse.ArgumentParser(description="dsg_lib endpoint benchmark")
    parser.add_argument("--requests", type=int, default=5000, help="requests per endpoint")
    parser.add_argument("--concurrency", type=int, default=50)
    parser.add_argument("--warmup", type=int, default=500)
    parser.add_argument(
        "--clients",
        type=int,
        default=max(1, min(8, (os.cpu_count() or 2) // 2)),
        help="load-generator processes (default: half the CPUs, at most 8)",
    )
    parser.add_argument("--frameworks", nargs="*", help="subset to run, e.g. fastapi")
    parser.add_argument("--log-messages", type=int, default=20000, help="0 skips the logging bench")
    parser.add_argument("--history", type=Path, default=HISTORY)
    parser.add_argument("--page", type=Path, default=PAGE)
    parser.add_argument("--no-write", action="store_true", help="print only; do not update the docs")
    parser.add_argument("--no-fail", action="store_true", help="report regressions but exit 0")
    args = parser.parse_args(argv)

    from dsg_lib import __version__

    commands = framework_commands()
    if args.frameworks:
        commands = {k: v for k, v in commands.items() if k in args.frameworks}
    skipped = sorted(set(args.frameworks or ["fastapi", "robyn"]) - set(commands))
    for name in skipped:
        print(f"skipping {name}: not installed for this Python")

    record = {
        "version": __version__,
        "git_sha": _git_sha(),
        "date": dt.date.today().isoformat(),
        **machine_profile(),
        "requests": args.requests,
        "concurrency": args.concurrency,
        "clients": args.clients,
        "frameworks": {},
    }
    for name, cmd in commands.items():
        print(f"benchmarking {name} ...")
        record["frameworks"][name] = bench_framework(
            name, cmd, args.requests, args.concurrency, args.warmup, args.clients
        )
    if args.log_messages:
        print("benchmarking logging ...")
        record["logging_us"] = run_logging_bench(args.log_messages)

    history = load_history(args.history)
    problems = compare(previous_on_same_profile(history, record), record)
    if not args.no_write:
        history.append(record)
        args.history.parent.mkdir(parents=True, exist_ok=True)
        args.history.write_text(json.dumps(history, indent=2) + "\n")
        args.page.write_text(render_page(history))
        print(f"wrote {args.history} and {args.page}")

    if problems:
        print("PERFORMANCE REGRESSION vs previous run on this machine:")
        for p in problems:
            print(f"  - {p}")
        return 0 if args.no_fail else 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
