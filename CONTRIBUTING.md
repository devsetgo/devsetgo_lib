# Contributing

Please feel to contribute to this project. Adding common functions is the intent and if you have one to add or improve an existing it is greatly appreciated.

### Ways to Contribute!
- Add or improve a function
- Add or improve documentation
- Add or improve Tests
- Report or fix a bug

### Performance

This library runs inside other people's applications, so its cost matters.
Before opening a PR that touches logging, the health or default endpoints, or
anything on a request path, run:

```bash
make logging-bench   # per-message logging cost, prints a table
make perf            # FastAPI + Robyn endpoint benchmark; appends to docs/performance/
make perf-smoke      # quick check that the benchmark harness itself still works
```

`make perf` exits with code 2 if `/api/health/status` regressed against the
previous run recorded on the same machine profile. `make bump` runs it
automatically (report-only) so every release gets a row in
`docs/performance/history.json`. `docs/performance/index.md` is generated from
that file; do not edit it by hand.
