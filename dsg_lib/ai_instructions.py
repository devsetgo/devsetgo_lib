# -*- coding: utf-8 -*-
"""
ai_instructions.py

Packaged, up-to-date integration instructions for AI coding assistants (GitHub
Copilot, Claude/Claude Code, or any other tool) that are helping a developer add
`devsetgo_lib` to an application. The instructions live here, in code, rather
than only in README/docs prose, so they can be:

    - Fetched programmatically by an agent via `get_app_instructions()`.
    - Generated as a file in the *consuming* application's repo (not this one)
      via the command-line entry point below, using the filename convention
      each tool looks for by default.

Command-line usage (run from the application repo that depends on
devsetgo_lib, not from this repo):

    python -m dsg_lib.ai_instructions                  # print generic instructions to stdout
    python -m dsg_lib.ai_instructions claude            # print the Claude-flavored copy
    python -m dsg_lib.ai_instructions claude --write     # write to ./CLAUDE.md
    python -m dsg_lib.ai_instructions copilot --write    # write to ./.github/copilot-instructions.md
    python -m dsg_lib.ai_instructions generic --write    # write to ./AI_INSTRUCTIONS.md
    python -m dsg_lib.ai_instructions claude --output docs/ai/CLAUDE.md

The three profiles ("generic", "copilot", "claude") carry the same
instructional content -- only the destination filename convention and a
one-line header differ -- since the guidance itself (correct function
signatures, exceptions, non-obvious gotchas) does not depend on which tool is
reading it.

Author: Mike Ryan
License: MIT
"""
import argparse
from pathlib import Path
from typing import Dict, Tuple

# Canonical profile names. Keep this in sync with _PROFILE_TO_FILENAME and
# _TOOL_LABEL below -- every profile must have an entry in both.
_CANONICAL_PROFILES: Tuple[str, ...] = ("generic", "copilot", "claude")

# Recognized aliases for the profile positional argument/get_app_instructions()
# argument, mapped to a canonical profile name above.
_PROFILE_ALIASES: Dict[str, str] = {
    "default": "generic",
    "ai": "generic",
    "generic-ai": "generic",
    "gpt": "generic",
    "chatgpt": "generic",
    "cursor": "generic",
    "codeium": "generic",
    "windsurf": "generic",
    "github-copilot": "copilot",
    "gh-copilot": "copilot",
    "vscode-copilot": "copilot",
    "anthropic": "claude",
    "claude-code": "claude",
}

# The filename convention each tool looks for by default in a repo root.
_PROFILE_TO_FILENAME: Dict[str, str] = {
    "generic": "AI_INSTRUCTIONS.md",
    "copilot": ".github/copilot-instructions.md",
    "claude": "CLAUDE.md",
}

_TOOL_LABEL: Dict[str, str] = {
    "generic": "any AI coding assistant",
    "copilot": "GitHub Copilot",
    "claude": "Claude / Claude Code",
}


def available_instruction_profiles() -> Tuple[str, ...]:
    """
    Return the canonical instruction profile names.

    Returns:
        Tuple[str, ...]: `('generic', 'copilot', 'claude')`. Aliases accepted
        by `get_app_instructions`/`suggested_instruction_filename` (e.g.
        `'anthropic'`, `'chatgpt'`, `'gh-copilot'`) are not included here --
        this is the canonical set they resolve to.
    """
    return _CANONICAL_PROFILES


def _normalize_profile(profile: str) -> str:
    """
    Resolve a user-supplied profile name or alias to a canonical profile name.

    Args:
        profile (str): A profile name or recognized alias, case-insensitive.

    Returns:
        str: One of `available_instruction_profiles()`.

    Raises:
        TypeError: If `profile` is not a string.
        ValueError: If `profile` (after alias resolution) is not a canonical
        profile name.
    """
    if not isinstance(profile, str):
        raise TypeError(f"profile must be a string, got {type(profile)}")

    key = profile.strip().lower()
    key = _PROFILE_ALIASES.get(key, key)

    if key not in _CANONICAL_PROFILES:
        raise ValueError(
            f"Unknown instruction profile: {profile!r}. "
            f"Valid profiles are: {', '.join(_CANONICAL_PROFILES)} "
            "(aliases such as 'anthropic', 'chatgpt', 'gh-copilot' are also accepted)."
        )
    return key


def suggested_instruction_filename(profile: str = "generic") -> str:
    """
    Return the conventional filename the given tool looks for in a repo root.

    Args:
        profile (str, optional): One of `available_instruction_profiles()`, or
        a recognized alias. Defaults to `"generic"`.

    Returns:
        str: `"AI_INSTRUCTIONS.md"` for generic, `".github/copilot-instructions.md"`
        for copilot, or `"CLAUDE.md"` for claude.

    Raises:
        ValueError: If `profile` is not a recognized profile or alias.

    Example:
    ```python
    from dsg_lib.ai_instructions import suggested_instruction_filename

    suggested_instruction_filename("claude")
    # 'CLAUDE.md'
    ```
    """
    return _PROFILE_TO_FILENAME[_normalize_profile(profile)]


def get_app_instructions(profile: str = "generic") -> str:
    """
    Return the packaged AI-assistant integration instructions for `profile`.

    This is the in-process equivalent of running
    `python -m dsg_lib.ai_instructions <profile>` -- use it when an agent
    already has this package importable and just needs the instruction text,
    without shelling out.

    Args:
        profile (str, optional): One of `available_instruction_profiles()`
        (`'generic'`, `'copilot'`, `'claude'`), or a recognized alias (e.g.
        `'anthropic'`, `'chatgpt'`). Defaults to `"generic"`.

    Returns:
        str: The full instructions text for that profile, ready to write
        verbatim to the file returned by `suggested_instruction_filename`.

    Raises:
        ValueError: If `profile` is not a recognized profile or alias.

    Example:
    ```python
    from dsg_lib.ai_instructions import get_app_instructions

    text = get_app_instructions("claude")
    print(text.splitlines()[0])
    # '# devsetgo_lib integration instructions (for Claude / Claude Code)'
    ```
    """
    canonical = _normalize_profile(profile)
    header = f"# devsetgo_lib integration instructions (for {_TOOL_LABEL[canonical]})\n\n"
    return header + _INSTRUCTIONS_BODY


def _resolve_output_path(destination: str, base_dir: Path) -> Path:
    """
    Resolve a CLI-supplied destination and confirm it stays within base_dir.

    Args:
        destination (str): A relative or absolute path supplied via `--output`
        or derived from `suggested_instruction_filename`.
        base_dir (Path): The directory the written file must stay within
        (normally the current working directory the CLI was invoked from).

    Returns:
        Path: The resolved, absolute destination path.

    Raises:
        ValueError: If the resolved path falls outside `base_dir` -- guards
        against a `--output ../../etc/whatever` style path escaping the
        intended application repo.
    """
    base_dir = base_dir.resolve()
    candidate = Path(destination)
    candidate = candidate if candidate.is_absolute() else base_dir / candidate
    candidate = candidate.resolve()

    try:
        candidate.relative_to(base_dir)
    except ValueError:
        raise ValueError(
            f"Refusing to write outside the current directory: {destination}"
        )
    return candidate


def main(argv=None) -> int:
    """
    Command-line entry point: `python -m dsg_lib.ai_instructions [profile] [options]`.

    Args:
        argv (list[str], optional): Argument list to parse instead of
        `sys.argv[1:]`. Primarily for testing.

    Returns:
        int: Process exit code (`0` on success).
    """
    parser = argparse.ArgumentParser(
        prog="python -m dsg_lib.ai_instructions",
        description=(
            "Print or write devsetgo_lib's AI assistant integration instructions. "
            "Run this from the application repo that depends on devsetgo_lib."
        ),
    )
    parser.add_argument(
        "profile",
        nargs="?",
        default="generic",
        help=(
            "Instruction profile: one of "
            f"{', '.join(available_instruction_profiles())} (aliases such as "
            "'anthropic'/'chatgpt'/'gh-copilot' also accepted). Defaults to 'generic'."
        ),
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help=(
            "Write the instructions to this profile's suggested filename "
            "(see suggested_instruction_filename()) instead of printing to stdout."
        ),
    )
    parser.add_argument(
        "--output",
        metavar="PATH",
        default=None,
        help=(
            "Write the instructions to an explicit path instead of stdout or the "
            "suggested filename. Must resolve inside the current directory."
        ),
    )
    args = parser.parse_args(argv)

    try:
        text = get_app_instructions(args.profile)
        destination = args.output or (
            suggested_instruction_filename(args.profile) if args.write else None
        )
    except (TypeError, ValueError) as exc:
        parser.error(str(exc))
        return 2  # pragma: no cover - argparse.error() already exits

    if destination is None:
        print(text)
        return 0

    try:
        target = _resolve_output_path(destination, Path.cwd())
    except ValueError as exc:
        parser.error(str(exc))
        return 2  # pragma: no cover - argparse.error() already exits

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
    print(f"Wrote {_normalize_profile(args.profile)} instructions to {target.relative_to(Path.cwd())}")
    return 0


_INSTRUCTIONS_BODY = '''\
Use these rules when integrating `devsetgo_lib` into an application. This is a
reusable-functions library (file I/O, logging, calendar/pattern helpers, email
validation, FastAPI endpoint helpers, async SQLAlchemy CRUD) -- **not** a
framework you build an app around. Import only the pieces you need.

Goal: produce correct integrations without reverse-engineering package
internals or guessing at parameter names/exception types.

## Package layout -- read this before importing anything

`devsetgo_lib` does **not** re-export functions at the top-level package
(`import dsg_lib` only gives you `dsg_lib.LOGGER`, `dsg_lib.__version__`, and
the `ai_instructions` helpers used to produce this document). Always import
from the specific submodule:

```python
from dsg_lib.common_functions import file_functions
from dsg_lib.common_functions import folder_functions
from dsg_lib.common_functions import file_mover
from dsg_lib.common_functions import logging_config
from dsg_lib.common_functions import calendar_functions
from dsg_lib.common_functions import email_validation
from dsg_lib.common_functions import patterns

from dsg_lib.fastapi_functions import http_codes
from dsg_lib.fastapi_functions import default_endpoints
from dsg_lib.fastapi_functions import system_health_endpoints

from dsg_lib.async_database_functions import database_config
from dsg_lib.async_database_functions import async_database
from dsg_lib.async_database_functions import database_operations
from dsg_lib.async_database_functions import base_schema
```

Do not invent a flatter import path (e.g. `from dsg_lib import file_functions`)
-- it does not exist and will raise `ImportError`.

## Output contract (for any non-trivial integration task)

- Correct imports from the submodule paths above (never guessed top-level names).
- Explicit `root_folder` handling for file operations -- see the file-functions
  section; a `root_folder` used on save must be repeated on open/delete.
- Real exception handling matched to what the function actually raises/returns
  (see "Error-handling model differs by module" below) -- do not wrap
  `email_validation`/`calendar_functions`/`async_database_functions` calls in
  `try/except` patterns that assume they raise when they instead return an
  error value.
- A short explanation of any non-obvious mapping/config choice (e.g. why a
  particular `SchemaBase*` mixin or `dns_type` was chosen).

## Error-handling model differs by module -- know which one you're in

This is the single most important thing to get right, because guessing wrong
produces code that *looks* correct but silently swallows or mishandles errors:

| Module | On invalid/failed input |
|---|---|
| `file_functions` | Raises `TypeError`/`ValueError` for bad arguments, `FileNotFoundError` for missing files. Real exceptions -- `try/except` is appropriate. |
| `folder_functions` | Mixed: `last_data_files_changed` catches everything and returns `(None, None)`; `make_folder`/`remove_folder` raise real exceptions. |
| `calendar_functions` | Never raises. Returns sentinel *strings* (`"Invalid month number"`, `"Invalid input, integer is required"`) or `-1` for bad input. Check the return value, not a try/except. |
| `email_validation` | Never raises for an invalid/undeliverable email -- returns a dict with `"valid": False` and `"error"/"error_type"` keys. Only raises `ValueError` for a bad `dns_type` argument. Check `result["valid"]`. |
| `patterns` | Raises `ValueError` only for empty/`None` delimiters; otherwise always returns a result dict (empty `"found"` list if nothing matched). |
| `async_database_functions.database_operations` | `DatabaseOperations` methods catch their own errors internally and return a `DatabaseErrorResult` (a `dict` subclass with `"error"`/`"details"` keys) instead of raising. Check `isinstance(result, DatabaseErrorResult)` after every call -- do not assume a raised exception will stop execution. `DBConfig.__init__` is the exception: it raises a plain `Exception` at construction time for unsupported config keys. |
| `fastapi_functions` | Standard FastAPI/Starlette semantics -- these are just router factories. |

## File operations (`dsg_lib.common_functions.file_functions`)

Functions: `save_json`/`open_json`, `save_csv`/`open_csv`/`append_csv`,
`save_text`/`open_text`, `delete_file`, plus `create_sample_files` for
generating CSV/JSON test fixtures.

Critical rule -- **`root_folder` must round-trip exactly**: every
`save_*`/`open_*`/`delete_file` function accepts an optional
`root_folder: str = None`. If you pass `root_folder="/some/path"` on save, you
must pass that *same* `root_folder` to `open_*`/`delete_file` to read or
delete it back -- there is no auto-discovery, and omitting it silently falls
back to the default `data/<type>` directory instead of raising.

```python
from dsg_lib.common_functions import file_functions

# Save and read back through the SAME root_folder.
file_functions.save_json("config.json", {"key": "value"}, root_folder="/app/data")
data = file_functions.open_json("config.json", root_folder="/app/data")
file_functions.delete_file("config.json", root_folder="/app/data")

# Without root_folder, all three default to data/json (relative to CWD).
file_functions.save_json("config.json", {"key": "value"})
data = file_functions.open_json("config.json")
```

Other rules:
- The `.json`/`.csv`/`.txt` extension is auto-appended on save if the caller
  omits it; `open_*` expect the extension already present in `file_name`.
- Filenames may not contain `/` or `\\` (raises `ValueError`); a non-string
  filename raises `TypeError`; a missing file on open/delete raises
  `FileNotFoundError`.
- `open_csv(file_name, delimiter=",", quote_level="minimal", skip_initial_space=True, root_folder=None, quotechar=None)`
  -- `quote_level` must be one of `"none"`/`"minimal"`/`"all"` (case-insensitive).
  Do **not** pass `quotechar` to `open_csv`: passing anything other than `None`
  always raises `TypeError`, because quoting is controlled entirely through
  `quote_level`. (`save_csv`/`append_csv` *do* accept `quotechar` -- it is only
  `open_csv` that rejects it.)
- `append_csv(file_name, data, root_folder=None, delimiter=",", quotechar='"')`
  requires `data[0]` (the header row you pass) to match the existing file's
  header *exactly*, or it raises `ValueError`. There is no column-remapping.

## Folder operations (`dsg_lib.common_functions.folder_functions`)

- `last_data_files_changed(directory_path) -> (datetime | None, Path | None)`
  -- the newest **file** in a directory (subdirectories are ignored); returns
  `(None, None)` for an empty or nonexistent directory instead of raising.
- `get_directory_list(file_directory: str) -> list[Path]` -- immediate
  subdirectories only, resolved relative to the current working directory.
- `make_folder(file_directory) -> bool` -- **despite the `str` type hint in
  its signature, this function requires a `pathlib.Path` object, not a
  string.** It calls `.is_dir()`/`.name` on the argument internally; passing a
  plain string raises `AttributeError: 'str' object has no attribute 'is_dir'`.
  Always construct a `Path` first: `folder_functions.make_folder(Path("/app/data/new_dir"))`.
  Raises `FileExistsError` if the folder already exists, `ValueError` if the
  folder name contains `<>:"/\\|?*`.
- `remove_folder(file_directory: str) -> None` -- accepts a plain string (it
  wraps it in `Path(...)` internally, unlike `make_folder`). Uses `rmdir()`,
  so it only removes *empty* directories -- raises `OSError` on a non-empty
  one and `FileNotFoundError` if it doesn't exist.

## File mover (`dsg_lib.common_functions.file_mover`)

`process_files_flow(source_dir, temp_dir, final_dir, file_pattern, compress=False, max_iterations=None)`
watches `source_dir` for files matching a glob pattern (e.g. `"*.csv"`), moves
each to `temp_dir`, optionally zips it, then moves it to `final_dir`. **This
call blocks forever** (it wraps `watchfiles.watch`, which never returns)
unless you pass `max_iterations` -- run it in a background thread/process/task,
never inline in a request handler or startup coroutine you expect to return.
`max_iterations` exists primarily for tests and bounded batch runs.

## Logging (`dsg_lib.common_functions.logging_config`)

`config_log(...)` configures a `loguru` sink with size-based rotation,
age-based retention, and optional compression, and (by default,
`intercept_standard_logging=True`) redirects the stdlib `logging` module
into loguru.

```python
from dsg_lib.common_functions.logging_config import config_log
from loguru import logger

config_log(
    logging_directory="logs",
    log_name="app",
    logging_level="INFO",
    log_rotation="100 MB",
    log_retention="30 days",
    log_retention_check_interval=60,  # seconds between retention sweeps outside of a rotation
)

logger.info("app started")
```

Gotchas:
- Call `config_log()` **once, as early as possible** in application startup.
  When `intercept_standard_logging=True` (the default), it strips handlers
  from *every* currently-registered stdlib logger and sets `propagate`
  according to `log_propagate` -- calling it again later, or after another
  library/framework has attached its own handlers, undoes that library's
  logging setup.
- After `config_log()`, log through `from loguru import logger` in
  application code. This library's own internal logger
  (`dsg_lib.LOGGER`, a plain stdlib `logging.Logger` named `"devsetgo_lib"`)
  is a separate object used for the library's own internal log calls -- most
  of this package logs through it, but `file_mover.py` and `logging_config.py`
  itself log through loguru's global `logger` directly. Don't assume every
  module in this package shares one logger instance.
- Retention/rotation size and duration strings are parsed with simple
  suffix matching (`"100 MB"`, `"30 days"`, `"12 hours"`, `"5 minutes"`) --
  there is no support for combined units like `"1 day 12 hours"`.

## Calendar functions (`dsg_lib.common_functions.calendar_functions`)

- `get_month(month: int) -> str` -- 1-12 (or an integer-like float, e.g.
  `3.0`) -> full month name. Out-of-range returns the literal string
  `"Invalid month number"`; a non-integer, non-integer-like input returns
  `"Invalid input, integer is required"`. Neither case raises.
- `get_month_number(month_name: str) -> int` -- case-insensitive and
  whitespace-tolerant (internally `.strip().title()`-ed). Returns `-1` for an
  unrecognized name or a non-string input; never raises.

## Email validation (`dsg_lib.common_functions.email_validation`)

```python
from dsg_lib.common_functions import email_validation

result = email_validation.validate_email_address("user@example.com", check_deliverability=False)
if result["valid"]:
    normalized = result["email"]
else:
    print(result["error_type"], result["error"])
```

- Always check `result["valid"]` -- the function catches
  `EmailNotValidError`/`EmailUndeliverableError` internally and returns
  `{"valid": False, "email": ..., "error": str, "error_type": str, "parameters": dict}`
  rather than raising them. The only exception it actually raises is
  `ValueError`, and only when `dns_type` is neither `"dns"` nor `"timeout"`.
- `allow_display_name=True` is accepted for backward compatibility but is a
  documented **no-op** -- the pinned `email_validator` version has no such
  parameter on `validate_email`. Do not rely on it to permit display names;
  there is currently no way to opt into that through this function.
- `check_deliverability=True` (the default) performs a real DNS/MX lookup via
  `dns_type="dns"` (a cached resolver) or `"timeout"` (a resolver with an
  explicit timeout, default 5s if an invalid `timeout` is supplied). Pass
  `check_deliverability=False` for pure syntax validation in tests/CI where
  DNS lookups are undesirable.

## Pattern matching (`dsg_lib.common_functions.patterns`)

```python
from dsg_lib.common_functions import patterns

result = patterns.pattern_between_two_char("Hi 'John' and 'Jane'", "'", "'")
# result["found"] == ["John", "Jane"]
```

`pattern_between_two_char(text_string, left_characters, right_characters) -> dict`
returns `{"found": [...], "matched_found": int, "pattern_parameters": {...}}`.
Only the delimiter characters are regex-escaped -- captured substrings are
returned verbatim from the original text, even if they contain regex
metacharacters. Raises `ValueError` if either delimiter is `None` or empty;
never raises for "no matches" (returns `"found": []`).

## FastAPI helpers (`dsg_lib.fastapi_functions`)

```python
from fastapi import Depends, FastAPI, Header, HTTPException
from dsg_lib.fastapi_functions import default_endpoints, http_codes, system_health_endpoints

app = FastAPI()

# robots.txt, driven by a list of {"bot": str, "allow": bool} entries.
app.include_router(default_endpoints.create_default_router([
    {"bot": "Bingbot", "allow": False},
]))

# /status and /uptime are on by default; /heapdump defaults OFF because it
# discloses internal file paths and memory usage -- secure it with your own
# app auth dependency when you turn it on, this library does not supply one.
async def verify_admin(x_api_key: str = Header(...)):
    if x_api_key != "expected-secret":
        raise HTTPException(status_code=401, detail="Unauthorized")

health_config = {
    "enable_status_endpoint": True,
    "enable_uptime_endpoint": True,
    "enable_heapdump_endpoint": True,
    "heapdump_dependencies": [Depends(verify_admin)],
}
app.include_router(
    system_health_endpoints.create_health_router(health_config),
    prefix="/api/health",
    tags=["system-health"],
)

# Use the packaged HTTP-code dictionaries in `responses=` for cleaner OpenAPI docs.
@app.get("/items/{item_id}", responses=http_codes.generate_code_dict([404, 422]))
async def get_item(item_id: int):
    ...
```

- `http_codes` exposes `ALL_HTTP_CODES` (every code -> `{"description",
  "extended_description", "link"}`) plus pre-built `GET_CODES`, `POST_CODES`,
  `PUT_CODES`, `PATCH_CODES`, `DELETE_CODES` dicts, and the
  `generate_code_dict(codes, description_only=False)` helper used to build
  them. Use these directly in a route's `responses=` kwarg.
- `create_default_router(config)` only adds `/robots.txt` today -- don't
  assume it adds `/favicon.ico` or other default routes.
- `create_health_router(config)` recognized keys: `enable_status_endpoint`
  (default `True`), `enable_uptime_endpoint` (default `True`),
  `enable_heapdump_endpoint` (default `False`, opt-in), and
  `heapdump_dependencies` (a list of already-constructed FastAPI
  `Depends(...)` objects, only consulted when the heapdump endpoint is
  enabled).

## Async database functions (`dsg_lib.async_database_functions`)

Three layers, each wrapping the previous one -- build them in this order:

1. **`database_config.DBConfig(config: dict)`** -- validates `config` and
   builds the SQLAlchemy async engine + session factory. `config["database_uri"]`
   is required; every other key is checked against a dialect-specific
   allow-list (`DBConfig.SUPPORTED_PARAMETERS`) plus dialect-agnostic
   `DBConfig.COMMON_PARAMETERS` (`connect_args`, `execution_options`,
   `isolation_level`, `query_cache_size`, `hide_parameters`). An unsupported
   key for the detected dialect raises a plain `Exception` (not a subclass)
   **at construction time**, before any connection is attempted.
2. **`async_database.AsyncDatabase(db_config)`** -- exposes `.Base` (the
   shared `declarative_base()` every model must inherit from),
   `get_db_session()` (an async context manager yielding an `AsyncSession`),
   `create_tables()`, and `disconnect()`.
3. **`database_operations.DatabaseOperations(async_db)`** -- the CRUD layer.
   You still build the SQLAlchemy query yourself (via `sqlalchemy.select`/
   `insert`/`update`/`delete`); this class only handles session
   lifecycle, error capture, and result shaping.

```python
from sqlalchemy import Column, String, insert, select
from dsg_lib.async_database_functions import (
    async_database, base_schema, database_config, database_operations,
)

config = {
    "database_uri": "sqlite+aiosqlite:///:memory:?cache=shared",
    "echo": False,
    "future": True,
    "pool_recycle": 3600,
}
db_config = database_config.DBConfig(config)
async_db = async_database.AsyncDatabase(db_config)
db_ops = database_operations.DatabaseOperations(async_db)

class User(base_schema.SchemaBaseSQLite, async_db.Base):
    __tablename__ = "users"
    name = Column(String(50))

async def main():
    await async_db.create_tables()

    # execute_one/execute_many are the current API -- prefer them.
    result = await db_ops.execute_one(insert(User).values(name="John Doe"))
    # -> "complete" by default; pass return_metadata=True for rowcount/inserted_primary_key/rows.

    users = await db_ops.read_query(select(User))
    # -> list of User ORM instances (verified: db_ops.read_query(select(User))
    #    round-trips real rows in an in-memory SQLite session).

    page = await db_ops.paginate_query(select(User), page=1, page_size=25)
    # -> {"items": [...], "total": int, "page": 1, "page_size": 25, "pages": int}
```

Model base classes (`base_schema`): pick the mixin matching your target
database -- `SchemaBaseSQLite`, `SchemaBasePostgres`, `SchemaBaseMySQL`,
`SchemaBaseOracle`, `SchemaBaseMSSQL`, `SchemaBaseFirebird`, `SchemaBaseSybase`,
or `SchemaBaseCockroachDB`. Each provides `pkid` (UUID string primary key),
`date_created`, and `date_updated`. `SchemaBaseSQLite` stamps the timestamp
columns in Python (SQLite has no reliable server-side UTC function); every
other dialect stamps them via a server-side default expression -- don't use
the SQLite mixin against a non-SQLite database or vice versa.

`DatabaseOperations` method summary -- prefer the first group; the second
group still works but emits `DeprecationWarning`:

- Current: `execute_one(query, values=None, return_metadata=False)`,
  `execute_many(queries, return_results=False)`, `read_one_record(query)`
  (returns `None`, not an error, when nothing matches),
  `read_query(query)`, `read_multi_query({name: query, ...})`,
  `count_query(query)`, `paginate_query(query, page=1, page_size=100)`,
  `get_columns_details(table)`, `get_primary_keys(table)`,
  `get_table_names()`.
- Deprecated (each just wraps `execute_one`/`execute_many` and warns):
  `create_one`, `create_many`, `update_one`, `delete_one`, `delete_many`.
  Don't write new code against these -- use `execute_one`/`execute_many`
  with an explicit `insert`/`update`/`delete` statement instead.

Every method above (except `DBConfig.__init__`, which raises at construction)
catches its own errors and returns a `DatabaseErrorResult` -- a `dict`
subclass with `"error"` and `"details"` keys -- instead of letting the
underlying `SQLAlchemyError`/`IntegrityError` propagate:

```python
result = await db_ops.execute_one(insert(User).values(name=None))  # e.g. a NOT NULL violation
if isinstance(result, database_operations.DatabaseErrorResult):
    print(result["error"], result["details"])
```

`isinstance(result, DatabaseErrorResult)` is the correct check -- plain
`isinstance(result, dict)` is ambiguous whenever the real (non-error) result
is itself a dict, e.g. a multi-column row from `read_query`.

## Common mistakes to avoid

- Importing from the top-level `dsg_lib` package expecting re-exported
  functions -- import from the specific submodule instead (see "Package
  layout" above).
- Passing `root_folder` to `save_json`/`save_csv`/`save_text` but forgetting
  to pass the *same* `root_folder` to the matching `open_*`/`delete_file`
  call -- it silently falls back to the default directory instead of erroring.
- Passing a plain string to `folder_functions.make_folder` -- it needs a
  `pathlib.Path` despite its type hint.
- Wrapping `email_validation.validate_email_address` or
  `calendar_functions.get_month`/`get_month_number` calls in `try/except` to
  catch invalid input -- they don't raise for that; check the returned
  value/dict instead.
- Assuming `DatabaseOperations` methods raise on failure -- check
  `isinstance(result, DatabaseErrorResult)` instead of wrapping calls in
  `try/except SQLAlchemyError`.
- Writing new code against `create_one`/`create_many`/`update_one`/
  `delete_one`/`delete_many` -- use `execute_one`/`execute_many` with an
  explicit statement; the older methods are deprecated wrappers kept only
  for backward compatibility.
- Calling `file_mover.process_files_flow(...)` without `max_iterations` from
  code that expects it to return -- it blocks forever by design (a
  continuous directory watch); run it in a background task/thread/process.
- Calling `logging_config.config_log()` more than once, or after another
  library has already configured stdlib logging handlers -- it resets
  every registered logger's handlers on each call.
- Mixing a `SchemaBase<Dialect>` mixin with the wrong target database (e.g.
  using `SchemaBaseSQLite`'s Python-side timestamps against Postgres).

## Quality gates before completion

- Every `file_functions`/`folder_functions` call's exception handling matches
  the actual exception type that function raises (see the error-handling
  table above), not a guessed one.
- Every `root_folder` used on a save call is repeated on the matching
  open/delete call.
- Every `DatabaseOperations` call site checks
  `isinstance(result, DatabaseErrorResult)` rather than relying on a raised
  exception.
- New database CRUD code uses `execute_one`/`execute_many`, not the
  deprecated `create_one`/`create_many`/`update_one`/`delete_one`/`delete_many`.
- `config_log()` is called exactly once, near application startup.
- No placeholder/TODO code in the generated integration.

## Prompt templates

Simple integration: "Add devsetgo_lib file_functions to this app: save
[X] as JSON under a custom root_folder, and add the matching read/delete
calls using the same root_folder."

Database integration: "Set up devsetgo_lib async_database_functions for
this app against [SQLite/Postgres/...]: a DBConfig + AsyncDatabase +
DatabaseOperations, one model using the matching SchemaBase<Dialect> mixin,
and CRUD routes using execute_one/execute_many (not the deprecated
create_one/update_one/delete_one)."

FastAPI integration: "Wire up devsetgo_lib's default_endpoints (robots.txt)
and system_health_endpoints (status/uptime, heapdump behind our existing
auth dependency) into this FastAPI app, using http_codes.generate_code_dict
for the responses= on our existing routes."
'''


if __name__ == "__main__":
    raise SystemExit(main()) # no pragma: no cover - only run when invoked as a script
