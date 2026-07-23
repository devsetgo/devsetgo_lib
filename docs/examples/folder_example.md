# folder_example Example

# Folder Example Module

Demonstrates `dsg_lib.common_functions.folder_functions`: `make_folder`,
`get_directory_list`, `last_data_files_changed`, and `remove_folder`.

## Functions

### `create_workspace(base_dir: Path) -> Path`
Creates a new folder under `base_dir` using `make_folder`, and shows the
`FileExistsError` it raises on a repeat call.

### `list_subfolders(base_dir: Path) -> list`
Lists the subfolders of `base_dir` using `get_directory_list`.

### `find_last_changed_file(directory: Path)`
Writes a couple of files into a directory, then finds the most recently
modified one with `last_data_files_changed`.

### `cleanup_workspace(folder: Path) -> None`
Removes an empty folder using `remove_folder`, and shows the `OSError` it
raises when the folder still has files in it.

## Usage

Run the module directly to create a folder, list directories, find the most
recently changed file, and clean up -- including the two error paths
(`FileExistsError` from a duplicate `make_folder`, `OSError` from removing a
non-empty folder).

## Example Execution

```bash
python folder_example.py
```
## License
This module is licensed under the MIT License.

```python
import time
from pathlib import Path

from dsg_lib.common_functions.folder_functions import (
    get_directory_list,
    last_data_files_changed,
    make_folder,
    remove_folder,
)

BASE_DIR: Path = Path.cwd() / "data" / "folder_example"


def create_workspace(base_dir: Path) -> Path:
    """
    Create a new folder under `base_dir`, then show that creating it again
    raises `FileExistsError`.

    Args:
        base_dir (Path): The parent directory to create the workspace in.

    Returns:
        Path: The path to the newly created folder.
    """
    base_dir.mkdir(parents=True, exist_ok=True)
    workspace = base_dir / "workspace"

    if workspace.is_dir():
        remove_folder(workspace)  # start from a clean state on repeat runs

    make_folder(workspace)
    print(f"Created folder: {workspace}")

    try:
        make_folder(workspace)
    except FileExistsError as e:
        print(f"Handled error creating a duplicate folder: {e}")

    return workspace


def list_subfolders(base_dir: Path) -> list:
    """
    List the subfolders of `base_dir`.

    Args:
        base_dir (Path): The directory to list subfolders of.

    Returns:
        list: The subfolders of `base_dir`, as returned by `get_directory_list`.
    """
    return get_directory_list(str(base_dir))


def find_last_changed_file(directory: Path):
    """
    Write two files a moment apart, then report the most recently modified one.

    Args:
        directory (Path): The directory to write files into and inspect.

    Returns:
        Tuple[datetime, Path]: The modification time and path of the newest file.
    """
    (directory / "first.txt").write_text("created first")
    time.sleep(0.01)
    (directory / "second.txt").write_text("created second")

    return last_data_files_changed(directory)


def cleanup_workspace(folder: Path) -> None:
    """
    Remove `folder`, and show that removing a non-empty folder raises `OSError`.

    Args:
        folder (Path): The folder to remove. Must be empty to succeed.
    """
    try:
        remove_folder(folder)
    except OSError as e:
        print(f"Handled error removing a non-empty folder: {e}")
        for child in folder.iterdir():
            child.unlink()
        remove_folder(folder)
        print(f"Removed folder after clearing its contents: {folder}")


if __name__ == "__main__":
    print("Creating a workspace folder...")
    workspace_dir = create_workspace(BASE_DIR)

    print("\nListing subfolders...")
    print(list_subfolders(BASE_DIR))

    print("\nFinding the most recently changed file...")
    timestamp, newest_file = find_last_changed_file(workspace_dir)
    print(f"Newest file: {newest_file} (changed at {timestamp})")

    print("\nCleaning up...")
    cleanup_workspace(workspace_dir)
```
