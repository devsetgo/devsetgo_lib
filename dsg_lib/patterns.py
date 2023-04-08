import logging
import re

# Set up logging configuration
log_format = {
    "asctime": "%(asctime)s [UTC%(z)s]",
    "name": "%(name)s",
    "levelname": "%(levelname)s",
    "message": "%(message)s",
}
logging.basicConfig(format=log_format, level=logging.INFO)


def pattern_between_two_char(
    text_string: str, left_characters: str, right_characters: str
) -> dict:
    """
    This function searches for any substring that occurs between two specified characters in a given text string.
    It returns a dictionary containing the found substring(s), the number of matches found, and the regex pattern
    used to search for these matches.

    Parameters:
    -----------
        text_string : str
            Text string to be searched for matching substrings.
        left_characters : str
            The opening character that identifies the start of the target substring.
        right_characters : str
            The closing character that identifies the end of the target substring.

    Returns:
    --------
        Dictionary with the following keys:
        - 'found': A list of all matching substrings found.
        - 'matched_found': The number of matched substrings found (can be zero).
        - 'pattern_parameters': A dictionary containing the regex pattern used and the original input parameters.

    Example:
    ---------
    # Finding all strings between single quotes in the given string
    >>> pattern_between_two_char("This is a 'test' string with 'multiple' quotes.", "'", "'")
    {'found': ['test', 'multiple'], 'matched_found': 2, 'pattern_parameters':
     {'left_character': "\'", 'right_character': "\'", 'regex_pattern': "'(.+?)'?", 'text_string':
     'This is a \'test\' string with \'multiple\' quotes.'}}
    """

    try:
        # Check if left character is an alphanumeric
        if not left_characters.isalnum():
            raise ValueError("The left character is not alphanumeric and cannot be used.")

        # Check if right character is an alphanumeric
        if not right_characters.isalnum():
            raise ValueError("The right character is not alphanumeric and cannot be used.")
        
        # Escape input strings to safely use it in regex pattern
        esc_text = re.escape(text_string)
        esc_left_char = re.escape(left_characters)
        esc_right_char = re.escape(right_characters)

        # Create a regex pattern that matches all substrings between target characters
        pattern = f"{esc_left_char}(.+?){esc_right_char}?"

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
            logging.debug(f"Matched pattern(s): {pattern_list}")

        # Log successful function execution using 'info' log level
        logging.info(f"Successfully executed 'pattern_between_two_char' function")

        return results

    except ValueError as e:
        # capture exception and return error in case of invalid input parameters
        results: dict = {
            "Error": str(e),
            "matched_found": 0,
            "pattern_parameters": {
                "left_character": left_characters,
                "right_character": right_characters,
                "regex_pattern": None,
                "text_string": text_string,
            },
        }
        # logging of regex error using 'critical' log level
        logging.critical(f"Failed to generate regex pattern with error: {e}")
        return results
