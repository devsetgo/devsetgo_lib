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

Every single message write triggers `rotate_logs()` (cheap `os.path.getsize` stat) *and* `apply_retention()`, which does `os.listdir()` on the log directory plus an `os.path.getmtime()` per matching file — under a global multiprocessing lock. At real logging volume this is a per-line O(n) directory walk serialized across all processes. Retention only needs to run periodically (time-based check, or only right after a rotation happens), not on every write.

### `calendar_functions.py:74-87, 122-135` — month tables rebuilt on every call

`months` tuple and `month_dict` are recreated inside `get_month`/`get_month_number` on each invocation. Trivial per-call cost, but these are pure constants — hoist to module level.

## Refactoring / consistency

- **`file_functions.py`** — `delete_file`, `save_json`, `save_csv`, `save_text` each re-implement the same "validate filename doesn't contain `/`/`\\`, ensure extension, mkdir target, build path" logic slightly differently (some raise `TypeError`, some `ValueError`, for the same class of violation). Worth extracting a shared `_safe_target_path(file_name, ext, root_folder)` helper — would also fix the round-trip gap above in one place.
- **`open_csv`** rejects `quotechar` via `**kwargs` sniffing (`if "quotechar" in kwargs: raise TypeError(...)`) instead of just not accepting it as a parameter — the kwargs catch-all serves no other purpose here and reads like leftover signature surface.
- **`folder_functions.py:82`** — `last_data_files_changed` uses `max((f.stat().st_mtime, f) for f in directory_path.iterdir())`, which calls `.stat()` on every entry including subdirectories; fine for flat dirs but will misbehave if a directory happens to be the newest-mtime entry (returns a dir path, not a file). Worth filtering to `if f.is_file()`.
- **`file_mover.py`** looks solid — clear separation of flow vs. per-file logic, proper use of `islice` for bounded iteration, docstrings accurate. No issues found.

## Opportunities to extend

- `save_json`/`open_json` don't expose `indent` or `ensure_ascii` — commonly wanted for human-readable output or non-ASCII data.
- `append_csv` requires exact header match; a `columns` remap or `ignore_header_mismatch` flag would make it usable when schemas drift slightly.
- No async variants anywhere in this module — if the rest of the library leans FastAPI/async, file I/O here is all synchronous and would block an event loop if called from async code.
