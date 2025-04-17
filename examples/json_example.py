# -*- coding: utf-8 -*-
"""
# JSON Example Module

This module demonstrates how to use the `open_json` and `save_json` functions from the `dsg_lib.common_functions.file_functions` package. It provides an example JSON structure and functions to save and load JSON data to and from a file.

## Features

- **Example JSON Data**: Contains a dictionary with information about historical figures and their contributions.
- **Save JSON Data**: Demonstrates saving JSON data to a file using the `save_json` function.
- **Open JSON Data**: Demonstrates loading JSON data from a file using the `open_json` function.

## Example JSON Structure

The `example_json` dictionary includes:
- A list of `super_cool_people` with details such as:
  - `name`: The name of the person.
  - `famous_for`: A brief description of their contributions.
  - `birth_date`: Their date of birth.
  - `death_date`: Their date of death.
- A `sources` field indicating the source of the information.

## Functions

### `save_some_data(example_json: Dict[str, Any])`
Saves the provided JSON data to a file named `your-file-name.json`.

### `open_some_data(the_file_name: str) -> Dict[str, Any]`
Loads JSON data from the specified file and returns it as a dictionary.

### `save_list_json(data: list, file_name: str)`
Saves a list of dictionaries as JSON to the specified file.

### `open_list_json(file_name: str) -> list`
Loads a list of dictionaries from the specified JSON file.

### `try_open_nonexistent_json(file_name: str)`
Attempts to open a non-existent JSON file and handles the error.

## Usage

Run the module directly to:
1. Save the `example_json` data to a file.
2. Load the data back from the file.
3. Save and load a list of dictionaries.
4. Attempt to open a non-existent file.

## Notes

- Ensure the `dsg_lib` package is installed and accessible in your environment.
- Replace `"your-file-name.json"` with the desired file name when using the functions in a real-world scenario.

## Example Execution

```bash
python json_example.py
```
## License
This module is licensed under the MIT License.
"""
from typing import Any, Dict

from dsg_lib.common_functions.file_functions import open_json, save_json

example_json: Dict[str, Any] = {
    "super_cool_people": [
        {
            "name": "Blaise Pascal",
            "famous_for": "Blaise Pascal was a French mathematician, physicist, inventor, writer and Catholic theologian. He was a child prodigy who was educated by his father, a tax collector in Rouen. Pascal's earliest work was in the natural and applied sciences where he made important contributions to the study of fluids, and clarified the concepts of pressure and vacuum by generalising the work of Evangelista Torricelli. Pascal also wrote in defence of the scientific method.",  # noqa: E501
            "birth_date": "Jun 19, 1623",
            "death_date": "Aug 19, 1662",
        },
        {
            "name": "Galileo Galilei",
            "famous_for": 'Galileo di Vincenzo Bonaulti de Galilei was an Italian astronomer, physicist and engineer, sometimes described as a polymath, from Pisa. Galileo has been called the "father of observational astronomy", the "father of modern physics", the "father of the scientific method", and the "father of modern science".',  # noqa: E501
            "birth_date": "Feb 15, 1564",
            "death_date": "Jan 08, 1642",
        },
        {
            "name": "Michelangelo di Lodovico Buonarroti Simoni",
            "famous_for": "Michelangelo di Lodovico Buonarroti Simoni , known best as simply Michelangelo, was an Italian sculptor, painter, architect and poet of the High Renaissance born in the Republic of Florence, who exerted an unparalleled influence on the development of Western art.",  # noqa: E501
            "birth_date": "Mar 06, 1475",
            "death_date": "Feb 18, 1564",
        },
    ],
    "sources": "wikipedia via Google search.",
}

def save_some_data(example_json: Dict[str, Any]) -> None:
    """
    Save the provided JSON data to a file named 'your-file-name.json'.

    Args:
        example_json (Dict[str, Any]): The JSON data to save.
    """
    save_json(file_name="your-file-name.json", data=example_json)

def open_some_data(the_file_name: str) -> Dict[str, Any]:
    """
    Load JSON data from the specified file.

    Args:
        the_file_name (str): The name of the JSON file to open.

    Returns:
        Dict[str, Any]: The loaded JSON data.
    """
    result: Dict[str, Any] = open_json(file_name=the_file_name)
    return result

# --- Additional Examples ---

simple_list_json: list = [
    {"id": 1, "value": "foo"},
    {"id": 2, "value": "bar"},
]

def save_list_json(data: list, file_name: str) -> None:
    """
    Save a list of dictionaries as JSON.

    Args:
        data (list): The list of dictionaries to save.
        file_name (str): The file name to save to.
    """
    save_json(file_name=file_name, data=data)

def open_list_json(file_name: str) -> list:
    """
    Load a list of dictionaries from a JSON file.

    Args:
        file_name (str): The file name to load from.

    Returns:
        list: The loaded list of dictionaries.
    """
    return open_json(file_name=file_name)

def try_open_nonexistent_json(file_name: str) -> None:
    """
    Attempt to open a non-existent JSON file and handle the error.

    Args:
        file_name (str): The file name to attempt to open.
    """
    try:
        open_json(file_name=file_name)
    except FileNotFoundError as e:
        print(f"Handled error: {e}")

if __name__ == "__main__":
    # Example 1: Save and load a complex dictionary
    print("Saving and loading example_json...")
    save_some_data(example_json)
    opened_file: Dict[str, Any] = open_some_data("your-file-name.json")
    print("Loaded example_json:", opened_file)

    # Example 2: Save and load a list of dictionaries
    print("\nSaving and loading a list of dictionaries...")
    save_list_json(simple_list_json, "list-example.json")
    loaded_list = open_list_json("list-example.json")
    print("Loaded list-example.json:", loaded_list)

    # Example 3: Attempt to open a non-existent file
    print("\nAttempting to open a non-existent file...")
    try_open_nonexistent_json("does_not_exist.json")
