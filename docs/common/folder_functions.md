# Folder Functions



==================
## last_data_files_changed
==================

This code defines a function `last_data_files_changed` which returns the last modified file's modification time and path from the given directory. If an error occurs while finding the last modified file, this function returns None for both modification time and path.

### How to Use
----------

To use this function, you need to pass the path of the directory as an argument.

```python
from pathlib import Path
from datetime import datetime
from typing import Tuple
from dsg_lib.folder_functions import last_data_files_changed

# provide directory path
directory_path = Path("/path/to/directory")

# call function to get last modified file's modification time and path
last_modified_time, last_modified_file_path = last_data_files_changed(directory_path)

if last_modified_time and last_modified_file_path:
    print(f"Last modified file in {directory_path} was {last_modified_file_path} modified at {last_modified_time}")
else:
    print(f"Error occurred while finding last modified file in {directory_path}")
```

#### Function Signature
------------------

```python
def last_data_files_changed(directory_path: pathlib.Path) -> Tuple[datetime.datetime, pathlib.Path]:
```

#### Input Parameters

*   `directory_path` (pathlib.Path): The directory path to search for the last modified file.

#### Output Parameters

*   `Tuple[datetime.datetime, pathlib.Path]`: A tuple containing the last modified file's modification time and path, or (None, None) if an error occurs.

#### Exceptions
----------

If any exception occurs while finding the last modified file, this function logs an error message and returns `(None, None)`.

#### Example
-------

```python

# provide directory path
directory_path = Path("/path/to/directory")

# call function to get last modified file's modification time and path
last_modified_time, last_modified_file_path = last_data_files_changed(directory_path)

if last_modified_time and last_modified_file_path:
    print(f"Last modified file in {directory_path} was {last_modified_file_path} modified at {last_modified_time}")
else:
    print(f"Error occurred while finding last modified file in {directory_path}")
```

This example code snippet will return the last modified file's modification time and path for the given directory path. If any exception occurs, it logs an error message and returns `(None, None)`.


===========================================
## get\_directory\_list
===========================================

This is a Python library function that returns a list of directories in a specified directory. The function takes one argument, the path to the directory to be searched. If the specified directory does not exist, the function raises a FileNotFoundError.

To use this function, import it into your Python script, then call it with the path to the directory you want to search. The function returns a list of directories within that directory.

Usage
-----

```python
from pathlib import Path
from dsg_lib.folder_functions import get_directory_list

# Call the function with the path to the directory you want to search
dir_list = get_directory_list('/path/to/directory')

# Print the list of directories
print(dir_list)
```

Arguments
---------

*   `file_directory` (str): The path to the directory to search for directories.

Returns
-------

The function returns a list of directories in the specified directory.

Raises
------

*   `FileNotFoundError`: If the specified directory does not exist.

Examples
--------

```python
# Import required libraries
import logging
from pathlib import Path
from get_directory_list import get_directory_list

# Set the directory to search
directory_path = Path.cwd().joinpath('my_directory')

# Get the list of directories in the specified directory
directory_list = get_directory_list(directory_path)

# Print the list of directories
print(directory_list)
```

This will output a list of all directories in the specified directory.


==============================================================
## make\_folder
==============================================================

This is a Python library function that creates a new folder in a specified directory. The function takes one argument, the path to the directory in which to create the new folder. If the specified folder already exists, the function raises a FileExistsError. If the folder name contains invalid characters, the function raises a ValueError.

To use this function, import it into your Python script, then call it with the path to the directory in which you want to create the new folder. The function returns a boolean value indicating whether the folder was created successfully.

Usage
-----

```python
from pathlib import Path
from dsg_lib.folder_functions import make_folder

# Call the function with the path to the directory in which you want to create the new folder
folder_created = make_folder(Path('/path/to/directory/new_folder'))

# Check if the folder was created successfully
if folder_created:
    print("Folder created successfully!")
```

Arguments
---------

*   `file_directory` (pathlib.Path): The directory in which to create the new folder.

Returns
-------

The function returns a boolean value indicating whether the folder was created successfully.

Raises
------

*   `FileExistsError`: If the folder already exists.
*   `ValueError`: If the folder name contains invalid characters.

Examples
--------

```python
# Import required libraries
import logging
from pathlib import Path
from dsg_lib.folder_functions import make_folder

# Set the directory in which to create the new folder
directory_path = Path.cwd().joinpath('my_directory')

# Set the name of the new folder to create
new_folder_name = 'new_folder'

# Create the path to the new folder
new_folder_path = directory_path.joinpath(new_folder_name)

# Create the new folder
make_folder(new_folder_path)

# Log a message indicating that the new folder was created successfully
logging.info(f"New folder created: {new_folder_path}")
```

This will create a new folder named "new\_folder" within the "my\_directory" directory. If the new folder is created successfully, the function will log a message indicating that the new folder was created.


================================================================
## remove\_folder
================================================================

This is a Python library function that removes a folder from a specified directory. The function takes one argument, the path to the directory containing the folder to be removed. If the specified directory does not exist, the function raises a FileNotFoundError. If the folder could not be removed, the function raises an OSError.

To use this function, import it into your Python script, then call it with the path to the directory containing the folder to be removed. The function does not return any values.

Usage
-----

```python
from dsg_lib.folder_functions import remove_folder

# Call the function with the path to the directory containing the folder to be removed
remove_folder('/path/to/directory/folder_to_remove')
```

Arguments
---------

*   `file_directory` (str): The directory containing the folder to be removed.

Returns
-------

The function does not return any values.

Raises
------

*   `FileNotFoundError`: If the specified directory does not exist.
*   `OSError`: If the folder could not be removed.

Examples
--------

```python
# Import required libraries
import logging
from pathlib import Path
from dsg_lib.folder_functions import remove_folder

# Set the path to the folder to be removed
folder_to_remove = Path.cwd().joinpath('my_directory', 'folder_to_remove')

# Remove the folder
remove_folder(folder_to_remove)

# Log a message indicating that the folder was removed successfully
logging.info(f"Folder removed: {folder_to_remove}")
```

This will remove the folder named "folder\_to\_remove" from the "my\_directory" directory. If the folder is removed successfully, the function will log a message indicating that the folder was removed.