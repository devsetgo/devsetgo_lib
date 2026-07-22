# Improvements: `dsg_lib/common_functions/`

Review of all 7 modules (~2,100 lines) for performance, refactoring, and capability gaps. Dated 2026-07-22.

## Bugs

### 1. `folder_functions.py:142-184` — dead nested function in `make_folder`

```python
def make_folder(file_directory):
    def make_folder(file_directory: str) -> bool:
        """...docstring only, no body..."""
    # actual logic runs here, in the OUTER function
    if file_directory.is_dir():
        ...
```

The inner `make_folder` is defined and immediately discarded on every call — it's never invoked. The real logic executes in the outer function's scope. Almost certainly a bad merge (docstring nested one level too deep). Functionally harmless today (outer body still runs), but allocates a throwaway function object every call and is confusing/fragile — the next edit is likely to "fix" it into the inner function and silently break the outer one.

**Status: fixed.**

### 2. `email_validation.py:134-143` — `allow_quoted_local` documented but silently dropped

`allow_quoted_local` is accepted in `validate_email_address`'s signature and documented, but was never passed into the underlying `validate_email(...)` call. Callers who passed `allow_quoted_local=True` got no effect.

`allow_display_name` is also accepted and documented, but — unlike `allow_quoted_local` — it turns out the installed `email_validator` (pinned `>=2.1.1,<3.0.0`) has no such parameter on `validate_email` at all; forwarding it raises `TypeError` on every single call. So this one isn't a "dropped parameter" bug, it's dead API surface: the flag has never done anything and can't be wired up without dropping support or switching validator libraries.

**Status: fixed.** `allow_quoted_local` is now forwarded to `validate_email`. `allow_display_name` is left as a documented no-op (docstring updated to say so explicitly) rather than silently pretending to work — removing it from the signature would be a breaking API change and is left for a separate decision.

### 3. `patterns.py:109-121` — `found` results can contain escaped text, not the original substring

The whole input string was regex-escaped before matching (`esc_text = re.escape(text_string)`), and `re.findall` ran against that escaped text — so captured groups reflected the *escaped* text. For plain text this was invisible, but if the delimited content contained any regex metacharacter (`.`, `(`, `+`, `*`, etc.), the returned `found` list contained backslash-escaped characters instead of the literal original substring — confirmed with `text_string="*c]", left="*", right="]"`, which returned `["c\\"]` instead of `["c"]`. This exact (wrong) output was baked into the test suite as the expected value.

Also removed the `pattern.replace(r"\w", r".")` line — it only ever fired if the *escaped* delimiter literally contained the two-character sequence `\w`, which essentially never happens in practice, and `.+?` already matches any character without it. Dead code with a misleading comment.

**Status: fixed.** Now only the delimiter characters are escaped to build the regex; matching runs against the original `text_string` directly, so captured substrings are returned verbatim. `tests/test_common_functions/test_pattern_between.py` updated: corrected the `*c]` case to expect `["c"]`, and added `test_pattern_between_two_char_metacharacters_in_content` covering metacharacters *inside* the captured content (e.g. `<a.b>c<d+e>` → `["a.b", "d+e"]`).

## API asymmetry (round-trip is broken)

`save_json`, `save_csv`, and `save_text` all took `root_folder`, but `open_json`, `open_csv`, `open_text`, and `delete_file` didn't — they were hardcoded to `data/<type>/`. If you saved to a custom `root_folder`, there was no way to read or delete that file through this module. Confirmed live in `docs/examples/csv_example.md`: `save_some_data` wrote with `root_folder="/data"`, but `open_some_data`/`delete_example_file` called `open_csv`/`delete_file` with no `root_folder` at all — the documented example did not actually work as written.

While implementing this, found a second, tightly-coupled bug in `save_text`: unlike `save_json`/`save_csv` (which write directly into `root_folder` when it's given, no subfolder), `save_text` unconditionally appended a `/text` subfolder onto `root_folder` — contradicting its own docstring example (`root_folder="/path/to/directory"` → claimed `'/path/to/directory/test.txt'`, actually wrote `'/path/to/directory/text/test.txt'`). A third bug in the same function: `file_path` was built from `file_name` *before* the `.txt` extension was appended, so files saved without an explicit `.txt` suffix were written with no extension at all, regardless of root_folder.

**Status: fixed.**
- Added `root_folder: str = None` to `open_json`, `open_csv`, `open_text`, and `delete_file`. When given, each reads/deletes directly from that folder — mirroring `save_json`/`save_csv`'s direct-placement semantics. When omitted, all four fall back to the same `data/<type>` defaults as before (no behavior change for existing callers).
- `save_text` now writes directly into `root_folder` when provided (no forced `/text` subfolder), matching `save_json`/`save_csv` and its own docstring. Default behavior (no `root_folder`) still resolves to `data/text`.
- `save_text` now appends the `.txt` extension before computing `file_path`, so the file written always has one, matching `open_text`'s documented expectation that filenames include the extension.
- `docs/examples/csv_example.md` updated so `open_some_data`/`delete_example_file` pass the same `root_folder="/data"` used by `save_some_data` — verified the full save → open → append → delete round-trip actually works end-to-end through a shared `root_folder`.
- New tests: round-trip tests (`save_* (root_folder=X)` → `open_*/delete_file(root_folder=X)`) for JSON, CSV, and text in `tests/test_common_functions/test_file_functions/`, plus a "root_folder must not silently fall back to the default" negative test for each. `test_save_text.py`'s existing test corrected — it had the old `/text`-subfolder-and-no-extension behavior baked in as expected.

## Performance

### `logging_config.py:136-149` — `SafeFileSink.__call__` does a full directory scan on every log line

Every single message write triggered `rotate_logs()` (cheap `os.path.getsize` stat) *and* `apply_retention()`, which does `os.listdir()` on the log directory plus an `os.path.getmtime()` per matching file — under a global multiprocessing lock. At real logging volume this was a per-line O(n) directory walk serialized across all processes.

**Status: fixed.**
- `SafeFileSink` now throttles `apply_retention()`: it runs immediately after an actual rotation (a new rotated file just appeared, so it's a natural time to prune old ones), and otherwise at most once per `retention_check_interval` seconds (new constructor param, default 60s) as a safety net for files that age out between rotations. `rotate_logs()` now returns `bool` so `__call__` knows whether a rotation just happened.
- `config_log()` gained a matching `log_retention_check_interval: float = 60` parameter, threaded through to `SafeFileSink`.
- While adding the first-ever test coverage for this class (it was 100% `# pragma: no cover` before), found and fixed a second, unrelated latent bug in `apply_retention()`: its filter (`filename.startswith(basename) and len(filename.split(".")) > 1`) also matched the *active* log file itself (`"app.log".split(".")` has length 2), meaning a quiet app whose log file went stale between writes could have retention delete the live file out from under it. Now explicitly skips the exact active-log-file name.
- New test file `tests/test_common_functions/test_logging_config_safe_file_sink.py` (17 tests, 97% coverage of `logging_config.py` — up from ~0% on `SafeFileSink`): `parse_size`/`parse_duration` parsing, `write_message`, `rotate_logs` (both branches, with and without compression, verifying the compressed archive's actual contents), `apply_retention` (removes stale rotated files, keeps recent ones, never touches the active log file), and three tests directly covering the throttling fix — no retention sweep across 50 rapid messages with no rotation, an immediate sweep right after a rotation, and a sweep once the interval elapses. 7 of the 17 tests verified to fail against the pre-fix code.

### `calendar_functions.py:74-87, 122-135` — month tables rebuilt on every call

`months` tuple and `month_dict` were recreated inside `get_month`/`get_month_number` on each invocation.

**Status: fixed.** Hoisted to module-level constants `MONTHS` (tuple) and `MONTH_NUMBERS` (dict, now derived from `MONTHS` via `enumerate` instead of being a separately-maintained literal, removing the duplication between the two lists). Pure refactor — existing tests pass unchanged, 100% coverage maintained.

## Refactoring / consistency

- **`file_functions.py`** — `delete_file`, `save_json`, `save_csv`, `save_text` each re-implemented the same "validate filename doesn't contain `/`/`\\`, ensure extension, mkdir target, build path" logic slightly differently (some raised `TypeError`, some `ValueError`, for the same class of violation).

  **Status: fixed.** Extracted `_validate_file_name(file_name)` (type + separator check) and `_safe_target_path(file_name, ext, root_folder, default_subdir)` (validation + extension + folder resolution/creation), and wired all four functions through them.
  - `save_csv`'s filename-with-`/`-or-`\\` case now raises `ValueError` (was `TypeError`) — brought in line with `save_json`/`save_text`/`delete_file`, which already treated "right type, wrong content" as a `ValueError`. `test_save_csv_with_invalid_file_name` updated to expect `ValueError`; added `test_save_csv_with_non_string_file_name` to keep the (unchanged) `TypeError`-for-non-string case covered.
  - `delete_file`'s separator check previously only tested `os.path.sep` (so on Linux a backslash in the filename slipped through) — now checks both `/` and `\\` like the others. Added `test_delete_invalid_filename_backslash` for this.
  - `save_json`/`save_csv` previously built their default folder from a hardcoded `"data/json"`/`"data/csv"` literal instead of the module-level `directory_to_files` variable, unlike `delete_file`/`open_json`/`open_csv`/`open_text`, which all honor it — meaning tests that patched `directory_to_files` for `save_json`/`save_csv` were silently patching nothing. Now routed through `directory_to_files` like the rest; behavior is unchanged since the default value is the same string.
  - Docstrings for `save_json`/`save_csv`/`save_text` updated to match: `save_csv`'s claimed-but-never-raised "ValueError if file name doesn't end with .csv" removed, `save_json`'s equivalent stale claim removed, `save_text`'s `Raises` section corrected to `ValueError` (was documented as `TypeError`) for the separator case.
- **`open_csv`** rejected `quotechar` via `**kwargs` sniffing (`if "quotechar" in kwargs: raise TypeError(...)`) instead of just not accepting it as a parameter.

  **Status: fixed.** Replaced `**kwargs` with an explicit `quotechar: str = None` parameter; passing it still raises `TypeError`, now self-documenting in the signature instead of via kwargs sniffing. No caller-visible behavior change — existing test (`test_open_csv_with_delimiter_and_quotechar`) passes unchanged.
- **`folder_functions.py:82`** — `last_data_files_changed` used `max((f.stat().st_mtime, f) for f in directory_path.iterdir())`, which calls `.stat()` on every entry including subdirectories; fine for flat dirs but would misbehave if a directory happened to be the newest-mtime entry (returns a dir path, not a file).

  **Status: fixed.** Filtered to `if f.is_file()`. Added `test_ignores_subdirectories`, which gives a subdirectory a newer mtime than any file and confirms the file is still returned; failed against the pre-fix code.
- **`file_mover.py`** looks solid — clear separation of flow vs. per-file logic, proper use of `islice` for bounded iteration, docstrings accurate. No issues found.

## Opportunities to extend

- `save_json`/`open_json` don't expose `indent` or `ensure_ascii` — commonly wanted for human-readable output or non-ASCII data.
- `append_csv` requires exact header match; a `columns` remap or `ignore_header_mismatch` flag would make it usable when schemas drift slightly.
- No async variants anywhere in this module — if the rest of the library leans FastAPI/async, file I/O here is all synchronous and would block an event loop if called from async code.
