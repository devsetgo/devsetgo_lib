Here's a user documentation for your module:

```markdown
# dsg_lib.common.file_functions

This module is part of the `dsg_lib.common` package. It provides functionality for saving and retrieving text data from files.

## Usage

To use the functions in this module, you need to import them from the `dsg_lib.common` package. Here's how you can do it:

```python
from dsg_lib.common.file_functions import save_text, open_text, save_json, open_json, save_csv, open_csv

```

### save_text(file_name: str, data: str, root_folder: str = None) -> str

This function saves a string of text to a file.

**Parameters:**

- `file_name` (str): The name of the file (excluding the extension).
- `data` (str): The text data to be saved.
- `root_folder` (str, optional): The root folder in which the file should be saved. Defaults to "data".

**Returns:**

- str: A string indicating that the file save is complete.

**Example:**

```python
from dsg_lib.common.file_functions import save_text

save_text('example', 'This is some example text.')
```

### open_text(file_name: str) -> str

This function opens a text file and returns its contents as a string.

**Parameters:**

- `file_name` (str): The name of the file to be opened.

**Returns:**

- str: The contents of the file as a string.

**Example:**

```python
from dsg_lib.common.file_functions import open_text

text = open_text('example')
print(text)  # Outputs: 'This is some example text.'
```

### save_json(file_name: str, data: dict, root_folder: str = None) -> str

This function saves a dictionary as a JSON file.

**Parameters:**

- `file_name` (str): The name of the file (excluding the extension).
- `data` (dict): The dictionary to be saved.
- `root_folder` (str, optional): The root folder in which the file should be saved. Defaults to "data".

**Returns:**

- str: A string indicating that the file save is complete.

**Example:**

```python
from dsg_lib.common.file_functions import save_json

data = {'key': 'value'}
save_json('example', data)
```

### open_json(file_name: str) -> dict

This function opens a JSON file and returns its contents as a dictionary.

**Parameters:**

- `file_name` (str): The name of the file to be opened.

**Returns:**

- dict: The contents of the file as a dictionary.

**Example:**

```python
from dsg_lib.common.file_functions import open_json

data = open_json('example')
print(data)  # Outputs: {'key': 'value'}
```


### save_csv(file_name: str, data: list, root_folder: str = None) -> str

This function saves a list of dictionaries as a CSV file.

**Parameters:**

- `file_name` (str): The name of the file (excluding the extension).
- `data` (list): The list of dictionaries to be saved.
- `root_folder` (str, optional): The root folder in which the file should be saved. Defaults to "data".

**Returns:**

- str: A string indicating that the file save is complete.

**Example:**

```python
from dsg_lib.common.file_functions import save_csv

data = [{'column1': 'value1', 'column2': 'value2'}, {'column1': 'value3', 'column2': 'value4'}]
save_csv('example', data)
```

### open_csv(file_name: str) -> list

This function opens a CSV file and returns its contents as a list of dictionaries.

**Parameters:**

- `file_name` (str): The name of the file to be opened.

**Returns:**

- list: The contents of the file as a list of dictionaries.

**Example:**

```python
from dsg_lib.common.file_functions import open_csv

data = open_csv('example')
print(data)  # Outputs: [{'column1': 'value1', 'column2': 'value2'}, {'column1': 'value3', 'column2': 'value4'}]
```


# dsg_lib.common.file_functions

This module is part of the `dsg_lib.common` package. It provides functionality for creating sample CSV and JSON files with random data.


## Usage

To use the functions in this module, you need to import them from the `dsg_lib.common.file_functions` package. Here's how you can do it:

```python
from dsg_lib.common.file_functions import create_sample_files
```

### create_sample_files(file_name: str, sample_size: int) -> None

This function creates sample CSV and JSON files with random data.

**Parameters:**

- `file_name` (str): The base name for the sample files (without extension).
- `sample_size` (int): The number of rows to generate for the sample files.

**Returns:**

- None

**Example:**

```python
from dsg_lib.common.file_functions import create_sample_files

create_sample_files('example', 100)
```

This will create `example.csv` and `example.json` files each with 100 rows of random data.


## Purpose

The purpose of this module is to provide a simple and efficient way to save and retrieve text data from files. It abstracts away the details of file handling, allowing you to focus on the data itself.