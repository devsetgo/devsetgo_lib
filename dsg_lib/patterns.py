# -*- coding: utf-8 -*-
import logging
import re

log_format = {
    "asctime": "%(asctime)s [UTC%(asctime:z)]",
    "name": "%(name)s",
    "levelname": "%(levelname)s",
    "message": "%(message)s",
}

logging.basicConfig(format=log_format, level=logging.INFO)


def pattern_between_two_char(
    text_string: str, left_characters: str, right_characters: str
) -> dict:
    try:
        if left_characters.isprintable() is False:
            raise ValueError("The left character is not printable and cannot be used.")

        if right_characters.isprintable() is False:
            raise ValueError("The right character is not printable and cannot be used.")

        esc_text = re.escape(text_string)
        esc_left_char = re.escape(left_characters)
        esc_right_char = re.escape(right_characters)

        pattern = f"{esc_left_char}(.+?){esc_right_char}+?"

        pattern_list = re.findall(pattern, esc_text)
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

        return results

    except ValueError as e:
        # capture exception and return results
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
        # logging of regex error
        logging.critical(results)
        return results
