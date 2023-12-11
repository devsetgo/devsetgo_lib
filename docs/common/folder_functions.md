# dsg_lib.common.folder_functions

This module is part of the `dsg_lib.common` package. It provides functionality for interacting with the file system, including getting the last modified file in a directory, getting a list of directories in a specified directory, creating a new folder, and removing a folder.

## Installation

This module is part of the `dsg_lib` package. To install the package, use pip:

```bash
pip install dsg_lib
```

## Usage

To use the functions in this module, you need to import them from the `dsg_lib.common.folder_functions` package. Here's how you can do it:

```python
from dsg_lib.common.folder_functions import last_data_files_changed, get_directory_list, make_folder, remove_folder
```

### last_data_files_changed(directory_path: pathlib.Path) -> Tuple[datetime.datetime, pathlib.Path]

This function gets the last modified file in a directory and returns its modification time and path.

**Parameters:**

- `directory_path` (pathlib.Path): The directory to search for the last modified file.

**Returns:**

- Tuple[datetime.datetime, pathlib.Path]: A tuple containing the modification time and path of the last modified file, or (None, None) if there was an error.

**Example:**

```python
from dsg_lib.common.folder_functions import last_data_files_changed
from pathlib import Path

directory_path = Path.cwd().joinpath('data/csv')
time_stamp, file_path = last_data_files_changed(directory_path)
```

### get_directory_list(file_directory: str) -> list

This function gets a list of directories in the specified directory.

**Parameters:**

- `file_directory` (str): The directory to search for directories.

**Returns:**

- list: A list of directories in the specified directory.

**Example:**

```python
from dsg_lib.common.folder_functions import get_directory_list

directories = get_directory_list('data/csv')
```

### make_folder(file_directory: pathlib.Path) -> bool

This function makes a folder in a specific directory.

**Parameters:**

- `file_directory` (pathlib.Path): The directory in which to create the new folder.

**Returns:**

- bool: True if the folder was created successfully, False otherwise.

**Example:**

```python
from dsg_lib.common.folder_functions import make_folder
from pathlib import Path

file_directory = Path.cwd().joinpath('data/new_folder')
make_folder(file_directory)
```

### remove_folder(file_directory: str)

This function removes a folder from the specified directory.

**Parameters:**

- `file_directory` (str): The directory containing the folder to be removed.

**Example:**

```python
from dsg_lib.common.folder_functions import remove_folder

remove_folder('data/new_folder')
```

## Purpose

The purpose of this module is to provide a simple and efficient way to interact with the file system. It abstracts away the details of file handling, allowing you to focus on your application logic.
