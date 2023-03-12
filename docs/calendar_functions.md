# Calendar Functions

## TODO:
- none


## Import
~~~python
# Import the function
from dsg_lib.calendar_functions import get_month,get_month_number
~~~



============================================
## get\_month() function
============================================

This function takes an integer `month` number between 1 and 12 and returns the corresponding month name as a string. If the input is not within the range of 1-12, it returns an "Invalid month number" error message.

Parameters
----------

### month: int

An integer between 1 and 12 representing the month number.

Returns
-------

The full name of the month corresponding to the input `month` number as a string. If the input is not within the range of 1-12, it returns an "Invalid month number" error message.

Example usage
-------------

```python

# Call the function with a valid input
month_name = get_month(4)
print(month_name) # Output: April

# Call the function with an invalid input
month_name = get_month(15)
print(month_name) # Output: Invalid month number
```


============================================
## get_month_number() function
============================================

This code defines a function `get_month_number()` that takes a month name as a string and returns the corresponding month number as an integer.

Usage
-----

### Function Signature

```python
def get_month_number(month_name: str) -> int:
```

### Inputs

*   `month_name` (str): A string containing the full name of a month.

### Outputs

*   (int): The month number corresponding to the input month name.
*   Returns -1 if the input is not a valid month name.

Example
-------

```python
>>> get_month_number("January")
1
>>> get_month_number("january")
1
>>> get_month_number("february")
2
>>> get_month_number("foo")
-1
```

Implementation details
----------------------

The function first creates a dictionary `month_dict` which maps month names to month numbers. It then sets up logging using the Python `logging` module.

If the input `month_name` is not a string, the function logs an error and returns -1. Otherwise, the function converts the input string to title case and removes any leading/trailing spaces. If the input `month_name` is a valid key in the dictionary, the function returns the corresponding month number. If the input `month_name` is not a valid key in the dictionary, the function logs an error and returns -1.