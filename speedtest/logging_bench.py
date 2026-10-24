# -*- coding: utf-8 -*-
"""
Logging micro-benchmark for dsg_lib.common_functions.logging_config.

Measures the per-message cost a host app pays for logging through this
library. Run from the repo root:

    python speedtest/logging_bench.py          # human-readable table
    python speedtest/logging_bench.py --json   # machine-readable, used by endpoint_bench.py

All numbers are single-process tight loops, so they are pessimistic compared to
bursty web traffic. Compare runs on the same machine only.
"""
import argparse
import json
import logging
import os
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from loguru import logger  # noqa: E402

from dsg_lib.common_functions.logging_config import SafeFileSink, config_log  # noqa: E402

MSG = "2026-01-01 00:00:00.000000 | INFO     | mod:func:1 - hello world message\n"


def _rate(fn, n):
    t0 = time.perf_counter()
    for _ in range(n):
        fn()
    dt = time.perf_counter() - t0
    return dt / n * 1e6  # microseconds per message


def run(n: int = 20_000) -> dict:
    """Run every benchmark and return {label: microseconds_per_message}."""
    results = {}
    cwd = os.getcwd()
    with tempfile.TemporaryDirectory(prefix="dsg_logbench_") as tmp:
        os.chdir(tmp)
        try:
            os.makedirs("log", exist_ok=True)
            sink = SafeFileSink("log/sink.log", "100 MB", "30 days", compression=None)
            results["sink_raw_write"] = _rate(lambda: sink(MSG), n)
            if hasattr(sink, "stop"):
                sink.stop()

            config_log(logging_directory="log", log_name="defaults", compression=None)
            results["loguru_info_defaults"] = _rate(lambda: logger.info("hello {}", 1), n)
            logger.complete()

            for enq in (True, False):
                config_log(
                    logging_directory="log",
                    log_name=f"e2e_{enq}",
                    logging_level="INFO",
                    enqueue=enq,
                    compression=None,
                )
                # The lambdas below take std=std / lib=lib as default args to
                # bind this iteration's logger (ruff B023).
                std = logging.getLogger("some.lib")
                lib = logging.getLogger("devsetgo_lib")
                results[f"loguru_info_enqueue_{enq}"] = _rate(
                    lambda: logger.info("hello {}", 1), n
                )
                results[f"stdlib_info_intercepted_enqueue_{enq}"] = _rate(
                    lambda std=std: std.info("hello %s", 1), n
                )
                results[f"stdlib_debug_discarded_enqueue_{enq}"] = _rate(
                    lambda std=std: std.debug("hello %s", 1), n
                )
                results[f"dsg_lib_debug_discarded_enqueue_{enq}"] = _rate(
                    lambda lib=lib: lib.debug("x %s", 1), n
                )
                logger.complete()

            for enq in (False, True):
                logger.remove()
                logger.add(lambda m: None, level="INFO", enqueue=enq)
                results[f"noop_sink_caller_cost_enqueue_{enq}"] = _rate(
                    lambda: logger.info("hello {}", 1), n
                )
                logger.complete()
        finally:
            logger.remove()
            os.chdir(cwd)
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("-n", type=int, default=20_000, help="messages per benchmark")
    parser.add_argument("--json", action="store_true", help="print JSON instead of a table")
    args = parser.parse_args()
    results = run(args.n)
    if args.json:
        print(json.dumps(results))
        return
    for label, us in results.items():
        print(f"{label:45s} {1e6 / us:>12,.0f} msg/s {us:9.2f} us/msg")


if __name__ == "__main__":
    main()
