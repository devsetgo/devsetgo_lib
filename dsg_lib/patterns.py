# -*- coding: utf-8 -*-
"""
patterns.py
-----------

This module provides a function `pattern_between_two_char` that searches for all patterns between two characters in a given string using regular expressions.

The function takes three arguments: the string to search, and the left and right characters that define the pattern. It returns a dictionary with details about the patterns found, including the number of matches and the regex pattern used for searching.

The function uses Python's built-in `re` module to perform the regex search. It also uses the `logger` module to log any errors that occur during execution, as well as the results of successful searches.

This module can be used in text processing tasks where you need to extract specific parts of a string based on surrounding characters. For example, you could use it to extract all words enclosed in quotes in a text file, or all HTML tags in a web page.

Example usage:

```python
from patterns import pattern_between_two_char

text = "Hello, my name is 'John Doe' and I live in 'New York'."
left_char = "'"
right_char = "'"

results = pattern_between_two_char(text, left_char, right_char)

print(results)
```

This will output:

```python
{
    'found': ['John Doe', 'New York'],
    'matched_found': 2,
    'pattern_parameters': {
        'left_character': "'",
        'right_character': "'",
        'regex_pattern': "'(.+?)'",
        'text_string': "Hello, my name is 'John Doe' and I live in 'New York'."
    }
}
```
"""
from loguru import logger
import re


def pattern_between_two_char(
    text_string: str, left_characters: str, right_characters: str
) -> dict:
    """
    Searches for all patterns between two characters (left and right) in a given string using regular expressions.

    Args:
        text_string: The string in which to search for patterns
        left_characters: The character(s) that appear(s) immediately to the left of the desired pattern
        right_characters: The character(s) that appear(s) immediately to the right of the desired pattern

    Returns:
        A dictionary with the following keys:
            - "found": a list of strings containing all patterns found
            - "matched_found": the number of patterns found
            - "pattern_parameters": a dictionary with the following keys:
                - "left_character": the escaped left character string used to build the regex pattern
                - "right_character": the escaped right character string used to build the regex pattern
                - "regex_pattern": the final regex pattern used for searching
                - "text_string": the escaped input string used for searching

        If an error occurs during execution, a dictionary with the following keys is returned instead:
            - "Error": a string containing the error message
            - "matched_found": 0
            - "pattern_parameters": a dictionary with the following keys:
                - "left_character": the original left character string passed as input
                - "right_character": the original right character string passed as input
                - "regex_pattern": None
                - "text_string": the original input string passed as input
    """

    if not left_characters or not right_characters:
        raise ValueError(
            f"Left '{left_characters}' and/or Right '{right_characters}' characters must not be None or empty"
        )

    try:
        # Escape input strings to safely use them in regex pattern
        esc_text = re.escape(text_string)
        esc_left_char = re.escape(left_characters)
        esc_right_char = re.escape(right_characters)

        # Create a regex pattern that matches all substrings between target characters
        pattern = f"{esc_left_char}(.+?){esc_right_char}"

        # Replace \w with . to match any printable UTF-8 character
        pattern = pattern.replace(r"\w", r".")

        # Search for all patterns and store them in pattern_list variable
        pattern_list = re.findall(pattern, esc_text)

        # Create a dictionary to store match details
        results: dict = {
            "found": pattern_list,
            "matched_found": len(pattern_list),
            "pattern_parameters": {
                "left_character": esc_left_char,
                "right_character": esc_right_char,
                "regex_pattern": pattern,
                "text_string": esc_text,
            },
        }

        # Log matched pattern(s) found using 'debug' log level
        if len(pattern_list) > 0:
            logger.debug(f"Matched pattern(s): {pattern_list}")

        # Log successful function execution using 'info' log level
        logger.info("Successfully executed 'pattern_between_two_char' function")
        return results

    except ValueError as e:  # pragma: no cover
        # capture exception and return error in case of invalid input parameters
        results: dict = {
            "error": str(e),
            "matched_found": 0,
            "pattern_parameters": {
                "left_character": left_characters,
                "right_character": right_characters,
                "regex_pattern": None,
                "text_string": text_string,
            },
        }
        # logger of regex error using 'critical' log level
        logger.critical(f"Failed to generate regex pattern with error: {e}")
        return results
