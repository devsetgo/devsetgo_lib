# -*- coding: utf-8 -*-
"""
This module contains functions for pattern searching in text using regular
expressions.

The main function in this module is `pattern_between_two_char`, which searches
for all patterns between two characters in a given string. The function uses
Python's built-in `re` module for regex searching and the `loguru` module for
logging.

Functions:
    pattern_between_two_char(text_string: str, left_characters: str,
    right_characters: str) -> dict:
        Searches for all patterns between two characters (left and right) in a
        given string using regular expressions.

Example:
    ```python from dsg_lib import patterns

    text = "Hello, my name is 'John Doe' and I live in 'New York'." left_char =
    "'" right_char = "'"

    results = patterns.pattern_between_two_char(text, left_char, right_char)

    print(results) ``` This will output: ```python {
        'found': ['John Doe', 'New York'], 'matched_found': 2,
        'pattern_parameters': {
            'left_character': "'", 'right_character': "'", 'regex_pattern':
            "'(.+?)'", 'text_string': "Hello, my name is 'John Doe' and I live
            in 'New York'."
        }
    }
    ```

"""
import re

from loguru import logger


def pattern_between_two_char(
    text_string: str, left_characters: str, right_characters: str
) -> dict:
    """
    Searches for all patterns between two characters (left and right) in a given
    string using regular expressions.

    This function takes a string and two characters as input, and returns a
    dictionary containing all patterns found between the two characters in the
    string. The dictionary also includes the number of matches found and the
    regex pattern used for searching.

    The function uses Python's built-in `re` module for regex searching and the
    `loguru` module for logging.

    Args:
        text_string (str): The string in which to search for patterns.
        left_characters (str): The character(s) that appear(s) immediately to
        the left of the desired pattern. right_characters (str): The
        character(s) that appear(s) immediately to the right of the desired
        pattern.

    Returns:
        dict: A dictionary with the following keys:
            - "found": a list of strings containing all patterns found.
            - "matched_found": the number of patterns found.
            - "pattern_parameters": a dictionary with the following keys:
                - "left_character": the escaped left character string used to
                  build the regex pattern.
                - "right_character": the escaped right character string used to
                  build the regex pattern.
                - "regex_pattern": the final regex pattern used for searching.
                - "text_string": the escaped input string used for searching.

    Example:
        ```python from dsg_lib import patterns

        text = "Hello, my name is 'John Doe' and I live in 'New York'."
        left_char = "'" right_char = "'"

        results = patterns.pattern_between_two_char(text, left_char, right_char)

        print(results) ``` This will output: ```python {
            'found': ['John Doe', 'New York'], 'matched_found': 2,
            'pattern_parameters': {
                'left_character': "'", 'right_character': "'", 'regex_pattern':
                "'(.+?)'", 'text_string': "Hello, my name is 'John Doe' and I
                live in 'New York'."
            }
        }
        ```
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

        # Create a regex pattern that matches all substrings between target
        # characters
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
