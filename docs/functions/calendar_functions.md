# dsg_lib.common.calendar_functions

This module provides a set of functions to convert between month numbers and their corresponding names. It is part of the `dsg_lib.common` package and is used for handling and converting between month numbers and names.

## Function: get_month

The `get_month` function takes an integer month number and returns the corresponding month name as a string.

### Parameters

- `month` (int): An integer between 1 and 12 representing the month number.

### Returns

- `str`: The full name of the month corresponding to the input month number. If the input is not within the range of 1-12, returns "Invalid month number". If the input is not an integer, returns "Invalid input, integer is required".

### Usage

```python
from dsg_lib.common.calendar_functions import get_month

# Get the name of the 1st month
print(get_month(1))  # Outputs: January

# Get the name of the 12th month
print(get_month(12))  # Outputs: December

# Try to get the name of an invalid month number
print(get_month(13))  # Outputs: Invalid month number

# Try to get the name of a month using a non-integer
print(get_month('January'))  # Outputs: Invalid input, integer is required
```

## Function: get_month_number

The `get_month_number` function takes a month name as a string and returns the corresponding month number as an integer.

### Parameters

- `month_name` (str): A string containing the full name of a month.

### Returns

- `int`: The month number corresponding to the input month name. If the input is not a valid month name, returns -1. If the input is not a string, returns "Invalid input, string is required".

### Usage

```python
from dsg_lib.common.calendar_functions import get_month_number

# Get the number of the month "January"
print(get_month_number("January"))  # Outputs: 1

# Get the number of the month "December"
print(get_month_number("December"))  # Outputs: 12

# Try to get the number of an invalid month name
print(get_month_number("InvalidMonth"))  # Outputs: -1

# Try to get the number of a month using a non-string
print(get_month_number(1))  # Outputs: Invalid input, string is required
```

These functions are useful when you have month numbers or names and you want to convert between them in a more human-readable format. They also validate the input to ensure it's a valid month number or name.