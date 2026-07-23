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

- `save_json`/`open_json` didn't expose `indent` or `ensure_ascii` — commonly wanted for human-readable output or non-ASCII data.

  **Status: fixed.** `save_json` gained `indent: int = None` and `ensure_ascii: bool = True` params, passed straight through to `json.dump` (defaults match `json.dump`'s own, so this is purely additive — no behavior change for existing callers). `open_json` needed no new parameters (`json.load` has no `indent`/`ensure_ascii` equivalent — it already parses either representation), but while wiring this up, both `save_json` and `open_json` were switched to explicit `encoding="utf-8"` (previously neither specified one, silently relying on the platform's locale-default text encoding). This was necessary, not cosmetic: `ensure_ascii=False` writes non-ASCII characters directly, and without a pinned UTF-8 encoding that write is only reliable on platforms whose locale default happens to be UTF-8 — e.g. it would raise `UnicodeEncodeError` on a Windows box defaulting to `cp1252`. New tests in `tests/test_common_functions/test_file_functions/test_save_json.py`: default output stays compact/ASCII-escaped (regression), `indent` produces multi-line output, `ensure_ascii=False` writes literal Unicode, and a combined round-trip through `open_json`. `examples/json_example.py` (and its generated `docs/examples/json_example.md`) gained a `save_pretty_unicode_json` example.
- `append_csv` required an exact header match; a `columns` remap or `ignore_header_mismatch` flag would make it usable when schemas drift slightly.

  **Status: fixed** (via the `columns` remap option — deliberately *not* an `ignore_header_mismatch` flag, since silently skipping validation risks writing misaligned data when column *order* differs from column *meaning*). `append_csv` gained `columns: Optional[List[str]] = None`: when given, `data` is data rows only (no header row), and `columns` names each row position. The function validates that `columns` is the same *set* of names as the file's existing header (raising `ValueError` listing any missing/extra names otherwise), then reorders each row from `columns`' order to the file's actual on-disk column order before appending — so a caller never has to reorder by hand, and a genuine mismatch (not just reordering) still raises instead of writing garbage. Omitting `columns` preserves the exact prior behavior (`data[0]` must match the existing header exactly). New tests in `tests/test_common_functions/test_file_functions/test_append_csv.py` cover: reordering onto a differently-ordered file, columns already in file order, a missing column, an extra/unknown column, and the unchanged no-`columns` exact-match path — 5 of these fail against the pre-fix code (`TypeError: unexpected keyword argument 'columns'`). `examples/csv_example.py` gained an `append_reordered_data` example (and its generated `docs/examples/csv_example.md`).

  While updating these examples, found that `examples/csv_example.py` and `examples/validate_emails.py` had **drifted from their own generated docs**: an earlier session's fixes (the `open_some_data`/`delete_example_file` `root_folder` round-trip fix from "API asymmetry" above, and the `allow_display_name` no-op note from bug #2) had been applied directly to `docs/examples/*.md` instead of to the `examples/*.py` source `scripts/update_docs.py` regenerates those docs from. Regenerating docs for this change would have silently reverted both fixes. Ported both fixes back into the `.py` sources so they now survive regeneration; confirmed via `git diff` that regenerating no longer touches `validate_emails.md` and only adds the new content to `csv_example.md`.
- No async variants anywhere in this module — if the rest of the library leans FastAPI/async, file I/O here is all synchronous and would block an event loop if called from async code.

  **Status: fixed.** Added `dsg_lib/common_functions/async_file_functions.py`, a thin async twin with identical function names/signatures for all 8 public `file_functions` functions (`delete_file`, `save_json`, `open_json`, `save_csv`, `append_csv`, `open_csv`, `save_text`, `open_text`). Each wraps its sync counterpart in `asyncio.to_thread` — no new dependency, no new error-handling paradigm, and deliberately *not* the `DatabaseErrorResult`-style catch-and-return pattern `async_database_functions` uses: exceptions (`TypeError`/`ValueError`/`FileNotFoundError`) propagate through the awaited call unchanged, since that's `asyncio.to_thread`'s default behavior. Docstrings on the async twins are deliberately short (defer to `file_functions.<name>` for full parameter/exception docs rather than duplicating the prose) — a direct lesson from the doc-drift bug found earlier in this same section (a fix applied only to a generated `.md` file, never its `.py` source, got silently reverted on regeneration); nothing duplicated means nothing to drift. `folder_functions.py`/`file_mover.py` were left out of scope (folder ops are cheap metadata calls; `file_mover.py`'s watch loop is a separate design problem). New test file `tests/test_common_functions/test_file_functions/test_async_file_functions.py` (27 tests, 100% coverage of the new module): delegation checks (mocked sync call, correct positional/keyword args), real round-trips via `tmp_path`, exception propagation per function, and a concurrency proof (a mocked, `time.sleep`-blocking sync call run concurrently with `asyncio.sleep` via `asyncio.gather`, confirming total elapsed time stays near the single blocking call's duration rather than their sum). `dsg_lib/ai_instructions.py` updated: import list, error-handling table, a new "Async file operations" section, a "common mistakes" entry, and — while there — also backfilled the `save_json`/`append_csv` descriptions with the `indent`/`ensure_ascii`/`columns` features from the two items above, which had never been added to that file. New docs page `docs/common_functions/async_file_functions.md` + `mkdocs.yml` nav entry, and a new dedicated example `examples/async_file_example.py` (kept separate from the format-specific `json_example.py`/`csv_example.py`/`text_example.py` rather than bolted onto them, so each example file keeps its single-purpose focus).
