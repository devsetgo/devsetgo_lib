# -*- coding: utf-8 -*-
"""
async_file_functions.py

Async twin of `file_functions.py`. Every function here has the identical
name and signature as its synchronous counterpart in
`dsg_lib.common_functions.file_functions`, and simply runs that sync
function in a worker thread via `asyncio.to_thread` so it can be awaited
from async code (e.g. a FastAPI handler) without blocking the event loop.

This module intentionally contains no independent logic: validation, path
resolution, and exception types (`TypeError`/`ValueError`/
`FileNotFoundError`) all live in `file_functions.py`, which remains the
single source of truth. See that module's docstrings for full parameter
and exception documentation -- the docstrings here are deliberately short,
to avoid two divergent copies of the same prose.

Functions (identical names/signatures to `file_functions.py`, all async):
    delete_file, save_json, open_json, save_csv, append_csv, open_csv,
    save_text, open_text

Example:
```python
import asyncio
from dsg_lib.common_functions import async_file_functions

async def main():
    await async_file_functions.save_json("test.json", {"key": "value"})
    data = await async_file_functions.open_json("test.json")
    print(data)

asyncio.run(main())
```

Author: Mike Ryan
Date: 2026/07/22
License: MIT
"""
import asyncio
from typing import List, Optional

from . import file_functions


async def delete_file(file_name: str, root_folder: str = None) -> str:
    """
    Async equivalent of `file_functions.delete_file`. Runs the sync call in
    a worker thread via `asyncio.to_thread`, so it is safe to `await` from
    an event loop without blocking it.

    See `file_functions.delete_file` for full parameter and exception
    documentation.

    Args:
        file_name (str): Name of the file to delete.
        root_folder (str, optional): Directory the file lives in. Defaults
            to the matching "data/<type>" directory.

    Returns:
        str: Same success message as `file_functions.delete_file`.

    Raises:
        TypeError: Same conditions as `file_functions.delete_file`.
        ValueError: Same conditions as `file_functions.delete_file`.
        FileNotFoundError: Same conditions as `file_functions.delete_file`.
    """
    return await asyncio.to_thread(
        file_functions.delete_file, file_name, root_folder=root_folder
    )


async def save_json(
    file_name: str,
    data,
    root_folder: str = None,
    indent: int = None,
    ensure_ascii: bool = True,
) -> str:
    """
    Async equivalent of `file_functions.save_json`. Runs the sync call in a
    worker thread via `asyncio.to_thread`, so it is safe to `await` from an
    event loop without blocking it.

    See `file_functions.save_json` for full parameter and exception
    documentation.

    Args:
        file_name (str): Name of the JSON file to save (".json" is
            appended if missing).
        data (list | dict): The data to serialize and save.
        root_folder (str, optional): Directory to save into. Defaults to
            "data/json".
        indent (int, optional): Indent width for pretty-printed output.
            Defaults to None (compact).
        ensure_ascii (bool, optional): Escape non-ASCII characters as
            `\\uXXXX` if True (default).

    Returns:
        str: Same success message as `file_functions.save_json`.

    Raises:
        TypeError: Same conditions as `file_functions.save_json`.
        ValueError: Same conditions as `file_functions.save_json`.
    """
    return await asyncio.to_thread(
        file_functions.save_json,
        file_name,
        data,
        root_folder=root_folder,
        indent=indent,
        ensure_ascii=ensure_ascii,
    )


async def open_json(file_name: str, root_folder: str = None) -> dict:
    """
    Async equivalent of `file_functions.open_json`. Runs the sync call in a
    worker thread via `asyncio.to_thread`, so it is safe to `await` from an
    event loop without blocking it.

    See `file_functions.open_json` for full parameter and exception
    documentation.

    Args:
        file_name (str): Name of the JSON file to open.
        root_folder (str, optional): Directory the file lives in. Defaults
            to "data/json".

    Returns:
        dict: Same contents as `file_functions.open_json`.

    Raises:
        TypeError: Same conditions as `file_functions.open_json`.
        FileNotFoundError: Same conditions as `file_functions.open_json`.
    """
    return await asyncio.to_thread(
        file_functions.open_json, file_name, root_folder=root_folder
    )


async def save_csv(
    file_name: str,
    data: list,
    root_folder: str = None,
    delimiter: str = ",",
    quotechar: str = '"',
) -> str:
    """
    Async equivalent of `file_functions.save_csv`. Runs the sync call in a
    worker thread via `asyncio.to_thread`, so it is safe to `await` from an
    event loop without blocking it.

    See `file_functions.save_csv` for full parameter and exception
    documentation.

    Args:
        file_name (str): Name of the CSV file to save (".csv" is appended
            if missing).
        data (list): Rows to save, including the header as the first row.
        root_folder (str, optional): Directory to save into. Defaults to
            "data/csv".
        delimiter (str, optional): Field separator. Defaults to ",".
        quotechar (str, optional): Quote character. Defaults to '"'.

    Returns:
        str: Same success message as `file_functions.save_csv`.

    Raises:
        TypeError: Same conditions as `file_functions.save_csv`.
        ValueError: Same conditions as `file_functions.save_csv`.
    """
    return await asyncio.to_thread(
        file_functions.save_csv,
        file_name,
        data,
        root_folder=root_folder,
        delimiter=delimiter,
        quotechar=quotechar,
    )


async def append_csv(
    file_name: str,
    data: list,
    root_folder: str = None,
    delimiter: str = ",",
    quotechar: str = '"',
    columns: Optional[List[str]] = None,
) -> str:
    """
    Async equivalent of `file_functions.append_csv`. Runs the sync call in
    a worker thread via `asyncio.to_thread`, so it is safe to `await` from
    an event loop without blocking it.

    See `file_functions.append_csv` for full parameter and exception
    documentation.

    Args:
        file_name (str): Name of the CSV file to append to.
        data (list): Rows to append. Header row required unless `columns`
            is given.
        root_folder (str, optional): Directory the file lives in. Defaults
            to "data/csv".
        delimiter (str, optional): Field separator. Defaults to ",".
        quotechar (str, optional): Quote character. Defaults to '"'.
        columns (List[str], optional): Column names for `data`'s rows when
            `data` has no header row. Defaults to None.

    Returns:
        str: Same success message as `file_functions.append_csv`.

    Raises:
        TypeError: Same conditions as `file_functions.append_csv`.
        ValueError: Same conditions as `file_functions.append_csv`.
        FileNotFoundError: Same conditions as `file_functions.append_csv`.
    """
    return await asyncio.to_thread(
        file_functions.append_csv,
        file_name,
        data,
        root_folder=root_folder,
        delimiter=delimiter,
        quotechar=quotechar,
        columns=columns,
    )


async def open_csv(
    file_name: str,
    delimiter: str = ",",
    quote_level: str = "minimal",
    skip_initial_space: bool = True,
    root_folder: str = None,
    quotechar: str = None,
) -> list:
    """
    Async equivalent of `file_functions.open_csv`. Runs the sync call in a
    worker thread via `asyncio.to_thread`, so it is safe to `await` from an
    event loop without blocking it.

    See `file_functions.open_csv` for full parameter and exception
    documentation.

    Args:
        file_name (str): Name of the CSV file to open.
        delimiter (str, optional): Field separator. Defaults to ",".
        quote_level (str, optional): One of "none"/"minimal"/"all".
            Defaults to "minimal".
        skip_initial_space (bool, optional): Defaults to True.
        root_folder (str, optional): Directory the file lives in. Defaults
            to "data/csv".
        quotechar (str, optional): Not supported -- passing anything other
            than None raises `TypeError`. Defaults to None.

    Returns:
        list: Same contents as `file_functions.open_csv`.

    Raises:
        TypeError: Same conditions as `file_functions.open_csv`.
        ValueError: Same conditions as `file_functions.open_csv`.
        FileNotFoundError: Same conditions as `file_functions.open_csv`.
    """
    return await asyncio.to_thread(
        file_functions.open_csv,
        file_name,
        delimiter=delimiter,
        quote_level=quote_level,
        skip_initial_space=skip_initial_space,
        root_folder=root_folder,
        quotechar=quotechar,
    )


async def save_text(file_name: str, data: str, root_folder: str = None) -> str:
    """
    Async equivalent of `file_functions.save_text`. Runs the sync call in a
    worker thread via `asyncio.to_thread`, so it is safe to `await` from an
    event loop without blocking it.

    See `file_functions.save_text` for full parameter and exception
    documentation.

    Args:
        file_name (str): Name of the text file to save (".txt" is appended
            if missing).
        data (str): The text data to save.
        root_folder (str, optional): Directory to save into. Defaults to
            "data/text".

    Returns:
        str: Same success message as `file_functions.save_text`.

    Raises:
        TypeError: Same conditions as `file_functions.save_text`.
        ValueError: Same conditions as `file_functions.save_text`.
    """
    return await asyncio.to_thread(
        file_functions.save_text, file_name, data, root_folder=root_folder
    )


async def open_text(file_name: str, root_folder: str = None) -> str:
    """
    Async equivalent of `file_functions.open_text`. Runs the sync call in a
    worker thread via `asyncio.to_thread`, so it is safe to `await` from an
    event loop without blocking it.

    See `file_functions.open_text` for full parameter and exception
    documentation.

    Args:
        file_name (str): Name of the text file to open.
        root_folder (str, optional): Directory the file lives in. Defaults
            to "data/text".

    Returns:
        str: Same contents as `file_functions.open_text`.

    Raises:
        TypeError: Same conditions as `file_functions.open_text`.
        FileNotFoundError: Same conditions as `file_functions.open_text`.
    """
    return await asyncio.to_thread(
        file_functions.open_text, file_name, root_folder=root_folder
    )
