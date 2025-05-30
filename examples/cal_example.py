# -*- coding: utf-8 -*-
"""
# Overview

This module demonstrates the usage of the `calendar_functions` module from the `dsg_lib.common_functions` package.
It provides examples of how to work with months, both by their numeric representation and their names.

The module includes two main functions:

1. **`calendar_check_number`**:
   - Iterates through a predefined list of month numbers (`month_list`) and uses the `get_month` function from `calendar_functions` to retrieve the corresponding month name.
   - It then prints the result for each number in the list.
   - Example:
     - Input: `1`
     - Output: `"January"`
     - Input: `13` (invalid)
     - Output: Depends on the implementation of `get_month` (e.g., `"Invalid Month"`).

2. **`calendar_check_name`**:
   - Iterates through a predefined list of month names (`month_names`) and uses the `get_month_number` function from `calendar_functions` to retrieve the corresponding numeric representation of the month.
   - It then prints the result for each name in the list.
   - Example:
     - Input: `"january"`
     - Output: `1`
     - Input: `"bob"` (invalid)
     - Output: Depends on the implementation of `get_month_number` (e.g., `"Invalid Month Name"`).

# Features

- **Validation of Inputs**:
  The module demonstrates how to handle invalid inputs, such as:
  - Numbers outside the valid range of months (1-12).
  - Invalid month names that do not correspond to any recognized month.

- **Testing and Debugging**:
  This module can be used to test and validate the robustness of the `calendar_functions` module by providing a variety of valid and invalid inputs.

# Usage

- Run the script directly to see the output of the two functions.
- Modify the `month_list` or `month_names` variables to test with different inputs.

# Dependencies

- **`dsg_lib.common_functions.calendar_functions`**:
  - This module must be available and contain the following functions:
    1. `get_month`: Accepts a numeric month (e.g., `1`) and returns the corresponding month name (e.g., `"January"`).
    2. `get_month_number`: Accepts a month name (e.g., `"january"`) and returns the corresponding numeric representation (e.g., `1`).

# Example Output

## For `calendar_check_number`:
If `month_list = [0, 1, 2, 3, 13]`, the output might be:
```
Invalid Month
January
February
March
Invalid Month
```

## For `calendar_check_name`:
If `month_names = ["january", "february", "bob"]`, the output might be:
```
1
2
Invalid Month Name
```

# Notes

- Ensure that the `calendar_functions` module is correctly implemented and imported.
- The behavior for invalid inputs depends on the implementation of `get_month` and `get_month_number`.

## License
This module is licensed under the MIT License.
"""
from dsg_lib.common_functions import calendar_functions
from typing import List, Any

# List of month numbers to test, including invalid values (0, 13)
month_list: List[int] = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]

# List of month names to test, including an invalid value ("bob")
month_names: List[str] = [
    "january",
    "february",
    "march",
    "april",
    "may",
    "june",
    "july",
    "august",
    "september",
    "october",
    "november",
    "december",
    "bob",
]

def calendar_check_number() -> None:
    """
    Example: Demonstrates converting month numbers to month names.
    Iterates through `month_list` and prints the result of get_month for each.
    """
    for i in month_list:
        month = calendar_functions.get_month(month=i)
        print(month)

def calendar_check_name() -> None:
    """
    Example: Demonstrates converting month names to month numbers.
    Iterates through `month_names` and prints the result of get_month_number for each.
    """
    for i in month_names:
        month = calendar_functions.get_month_number(month_name=i)
        print(month)

def calendar_check_float_and_invalid_types() -> None:
    """
    Example: Tests get_month with float values and various invalid types.
    Shows how the function handles non-integer and unexpected input types.
    """
    print("\nTesting get_month with float and invalid types:")
    test_values: List[Any] = [1.0, 12.0, 5.5, "3", None, [1], {"month": 2}]
    for val in test_values:
        print(f"Input: {val!r} -> Output: {calendar_functions.get_month(month=val)}")

def calendar_check_name_variants() -> None:
    """
    Example: Tests get_month_number with name variants and invalid types.
    Includes extra spaces, different cases, abbreviations, and non-string types.
    """
    print("\nTesting get_month_number with name variants and invalid types:")
    test_names: List[Any] = [
        " January ", "FEBRUARY", "mar", "Apr", "may", "JUNE", "July", "august", "Sept", "oct", "nov", "december",
        5, None, ["March"], {"month": "April"}
    ]
    for name in test_names:
        print(f"Input: {name!r} -> Output: {calendar_functions.get_month_number(month_name=name)}")

if __name__ == "__main__":
    # Run all example checks to demonstrate library usage and edge case handling
    calendar_check_number()
    calendar_check_name()
    calendar_check_float_and_invalid_types()
    calendar_check_name_variants()
