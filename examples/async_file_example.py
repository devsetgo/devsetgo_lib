# -*- coding: utf-8 -*-
"""
# Async File Example Module

Demonstrates `dsg_lib.common_functions.async_file_functions`, the async
twin of `file_functions`. Each call below is functionally identical to its
sync counterpart -- same names, same arguments, same exceptions -- just
awaitable, so it's safe to call from inside an async web handler (e.g. a
FastAPI route) without blocking the event loop.

## Functions

### `save_and_load_json() -> dict`
Saves and reloads a JSON payload using the async module.

### `save_and_load_csv() -> list`
Saves, appends to, and reloads CSV rows using the async module.

### `cleanup()`
Deletes the files created by the examples above.

## Usage

Run the module directly to save, reload, and then clean up both a JSON
and a CSV example file using only the async API.

## Example Execution

```bash
python async_file_example.py
```
## License
This module is licensed under the MIT License.
"""
import asyncio

from dsg_lib.common_functions import async_file_functions


async def save_and_load_json() -> dict:
    """
    Save a small JSON payload and immediately reload it, using only the
    async module.

    Returns:
        dict: The reloaded JSON data.
    """
    await async_file_functions.save_json(
        file_name="async-example.json", data={"key": "value"}
    )
    return await async_file_functions.open_json(file_name="async-example.json")


async def save_and_load_csv() -> list:
    """
    Save CSV rows, append one more row, then reload the file, using only
    the async module.

    Returns:
        list: The reloaded CSV data as a list of dictionaries.
    """
    rows = [["name", "value"], ["a", "1"]]
    await async_file_functions.save_csv(file_name="async-example.csv", data=rows)
    await async_file_functions.append_csv(
        file_name="async-example.csv", data=[["b", "2"]], columns=["name", "value"]
    )
    return await async_file_functions.open_csv(file_name="async-example.csv")


async def cleanup() -> None:
    """Delete the files created by the examples above."""
    await async_file_functions.delete_file("async-example.json")
    await async_file_functions.delete_file("async-example.csv")


async def main() -> None:
    print("Saving and loading JSON via async_file_functions...")
    print(await save_and_load_json())

    print("\nSaving, appending, and loading CSV via async_file_functions...")
    print(await save_and_load_csv())

    print("\nCleaning up example files...")
    await cleanup()


if __name__ == "__main__":
    asyncio.run(main())
