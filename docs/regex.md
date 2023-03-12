# RegEx Functions

### TODO:
- none

=================
## pattern_between_two_char
=================

DSG\_Lib.Patterns is a Python module that provides a function to search for a pattern between two characters in a given string.

### Usage
-----

#### `pattern_between_two_char(text_string: str, left_characters: str, right_characters: str) -> dict`

This function searches for a pattern between two characters in a given string.

##### Parameters

*   `text_string` (str): The string in which the pattern is searched.
*   `left_characters` (str): The left character used to specify the beginning of the pattern.
*   `right_characters` (str): The right character used to specify the end of the pattern.

##### Returns

This function returns a dictionary with the following keys:

*   `found` (list): A list of all patterns found.
*   `matched_found` (int): The number of patterns found.
*   `pattern_parameters` (dict): A dictionary with the following keys:
    *   `left_character` (str): The left character used to specify the beginning of the pattern.
    *   `right_character` (str): The right character used to specify the end of the pattern.
    *   `regex_pattern` (str): The regular expression pattern used to find the pattern.
    *   `text_string` (str): The string in which the pattern is searched.

If an error occurs during the search, the function returns a dictionary with the following keys:

*   `Error` (str): The error message.
*   `matched_found` (int): 0.
*   `pattern_parameters` (dict): A dictionary with the following keys:
    *   `left_character` (str): The left character used to specify the beginning of the pattern.
    *   `right_character` (str): The right character used to specify the end of the pattern.
    *   `regex_pattern` (str): None.
    *   `text_string` (str): The string in which the pattern is searched.

#### Example

```python
import dsg_lib.patterns as patterns

text = "Hello <world>! Goodbye <world>!"
left = "<"
right = ">"

result = patterns.pattern_between_two_char(text, left, right)

print(result)
```

Output:

```python
{
    "found": ["world", "world"],
    "matched_found": 2,
    "pattern_parameters": {
        "left_character": "\<",
        "right_character": "\>",
        "regex_pattern": "\<(.+?)\>+?",
        "text_string": "Hello \<world\>! Goodbye \<world\>!"
    }
}
```
