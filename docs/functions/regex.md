# dsg_lib.common.regex

This module is part of the `dsg_lib.common` package. It provides functionality for extracting patterns between two characters in a string using regular expressions.

## Installation

This module is part of the `dsg_lib` package. To install the package, use pip:

```bash
pip install dsg_lib
```

## Usage

To use the function in this module, you need to import it from the `dsg_lib.common.regex` package. Here's how you can do it:

```python
from dsg_lib.common.regex import pattern_between_two_char
```

### pattern_between_two_char(text_string: str, left_characters: str, right_characters: str) -> dict

This function searches for all patterns between two characters (left and right) in a given string using regular expressions.

**Parameters:**

- `text_string` (str): The string in which to search for patterns.
- `left_characters` (str): The character(s) that appear(s) immediately to the left of the desired pattern.
- `right_characters` (str): The character(s) that appear(s) immediately to the right of the desired pattern.

**Returns:**

- dict: A dictionary with the following keys:
    - "found": a list of strings containing all patterns found.
    - "matched_found": the number of patterns found.
    - "pattern_parameters": a dictionary with the following keys:
        - "left_character": the escaped left character string used to build the regex pattern.
        - "right_character": the escaped right character string used to build the regex pattern.
        - "regex_pattern": the final regex pattern used for searching.
        - "text_string": the escaped input string used for searching.

**Example:**

```python
from dsg_lib.common.regex import pattern_between_two_char

text = "Hello, my name is 'John Doe' and I live in 'New York'."
left_char = "'"
right_char = "'"

results = pattern_between_two_char(text, left_char, right_char)

print(results)
```

## Purpose

The purpose of this module is to provide a simple and efficient way to extract patterns between two characters in a string using regular expressions. It can be used in text processing tasks where you need to extract specific parts of a string based on surrounding characters.
