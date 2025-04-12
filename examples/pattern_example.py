# -*- coding: utf-8 -*-
"""
# Pattern Example Module

This module demonstrates the usage of the `pattern_between_two_char` function from the `dsg_lib.common_functions.patterns` package. It provides examples of how to extract patterns between specified characters in a given text block.

## Features

- **ASCII_LIST**: A comprehensive list of ASCII characters, which can be used for various text processing tasks.
- **pattern_find**: A utility function to find and pretty-print patterns between two specified characters in a text block.
- **run_examples**: A function that runs example use cases, including:
  - Extracting patterns from a simple text block.
  - Generating a large random text block and extracting patterns from it.

## Usage

To run the examples, execute this script directly. The output will demonstrate how patterns are extracted from text blocks.

## Functions

### `pattern_find(left_char: str, right_char: str, text_block: str)`
Finds and pretty-prints patterns between the specified `left_char` and `right_char` in the provided `text_block`.

### `run_examples()`
Runs example use cases to showcase the functionality of the `pattern_between_two_char` function.

## Example Output

When running the script, you will see:
1. Patterns extracted from a predefined text block.
2. Patterns extracted from a randomly generated large text block.

## License
This module is licensed under the MIT License.
"""
import pprint
from random import randint

from dsg_lib.common_functions.patterns import pattern_between_two_char

ASCII_LIST = [
    " ",
    "!",
    '""',
    "#",
    "$",
    "%",
    "&",
    "'",
    "(",
    ")",
    "*",
    "+",
    ",",
    "-",
    ".",
    "/",
    "0",
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    ":",
    ";",
    "<",
    "=",
    ">",
    "?",
    "@",
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
    "G",
    "H",
    "I",
    "J",
    "K",
    "L",
    "M",
    "N",
    "O",
    "P",
    "Q",
    "R",
    "S",
    "T",
    "U",
    "V",
    "W",
    "X",
    "Y",
    "Z",
    "[",
    "\\",
    "]",
    "^",
    "_",
    "`",
    "a",
    "b",
    "c",
    "d",
    "e",
    "f",
    "g",
    "h",
    "i",
    "j",
    "k",
    "l",
    "m",
    "n",
    "o",
    "p",
    "q",
    "r",
    "s",
    "t",
    "u",
    "v",
    "w",
    "x",
    "y",
    "z",
    "{",
    "|",
    "}",
    "~",
    "€",
    "‚",
    "ƒ",
    "„",
    "…",
    "†",
    "‡",
    "ˆ",
    "‰",
    "Š",
    "‹",
    "Œ",
    "Ž",
    "‘",
    "’",
    "“",
    "”",
    "•",
    "–",
    "—",
    "˜",
    "™",
    "š",
    "›",
    "œ",
    "ž",
    "Ÿ",
    "¡",
    "¢",
    "£",
    "¤",
    "¥",
    "¦",
    "§",
    "¨",
    "©",
    "ª",
    "«",
    "¬",
    "®",
    "¯",
    "°",
    "±",
    "²",
    "³",
    "´",
    "µ",
    "¶",
    "·",
    "¸",
    "¹",
    "º",
    "»",
    "¼",
    "½",
    "¾",
    "¿",
    "À",
    "Á",
    "Â",
    "Ã",
    "Ä",
    "Å",
    "Æ",
    "Ç",
    "È",
    "É",
    "Ê",
    "Ë",
    "Ì",
    "Í",
    "Î",
    "Ï",
    "Ð",
    "Ñ",
    "Ò",
    "Ó",
    "Ô",
    "Õ",
    "Ö",
    "×",
    "Ø",
    "Ù",
    "Ú",
    "Û",
    "Ü",
    "Ý",
    "Þ",
    "ß",
    "à",
    "á",
    "â",
    "ã",
    "ä",
    "å",
    "æ",
    "ç",
    "è",
    "é",
    "ê",
    "ë",
    "ì",
    "í",
    "î",
    "ï",
    "ð",
    "ñ",
    "ò",
    "ó",
    "ô",
    "õ",
    "ö",
    "÷",
    "ø",
    "ù",
    "ú",
    "û",
    "ü",
    "ý",
    "þ",
    "ÿ",
]

pp = pprint.PrettyPrinter(indent=4)


def pattern_find(left_char: str, right_char: str, text_block: str):
    data = pattern_between_two_char(text_block, left_char, right_char)
    pp.pprint(data)


def run_examples():
    text_block = "Lfound oneR Lfound twoR"
    left_char = "L"
    right_char = "R"
    pattern_find(left_char=left_char, right_char=right_char, text_block=text_block)

    for _ in range(100):
        long_input = "xyz" * randint(100, 100000)
        long_text = f"{long_input}abc<one>123<two>456<three>{long_input}"

        result = pattern_between_two_char(
            text_string=long_text, left_characters="<", right_characters=">"
        )
        print(result["found"])


if __name__ == "__main__":
    run_examples()
