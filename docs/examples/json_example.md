# json_example Example

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

### `save_some_data(example_json: str)`
Saves the provided JSON data to a file named `your-file-name.json`.

### `open_some_data(the_file_name: str) -> dict`
Loads JSON data from the specified file and returns it as a dictionary.

## Usage

Run the module directly to:
1. Save the `example_json` data to a file.
2. Load the data back from the file.
3. Print the loaded data to the console.

## Notes

- Ensure the `dsg_lib` package is installed and accessible in your environment.
- Replace `"your-file-name.json"` with the desired file name when using the functions in a real-world scenario.

## Example Execution

```bash
python json_example.py
```
## License
This module is licensed under the MIT License.

```python
from dsg_lib.common_functions.file_functions import open_json, save_json

example_json = {
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


def save_some_data(example_json: str):
    # function requires file_name and data as a string to be sent.
    # see documentation for additonal information
    save_json(file_name="your-file-name.json", data=example_json)


def open_some_data(the_file_name: str) -> dict:
    # function requires file_name and a string will be returned
    # see documentation for additonal information
    result: dict = open_json(file_name=the_file_name)
    return result


if __name__ == "__main__":
    save_some_data(example_json)
    opened_file: dict = open_some_data("your-file-name.json")
    print(opened_file)
```
