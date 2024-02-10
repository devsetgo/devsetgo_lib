# -*- coding: utf-8 -*-
import unittest

# from srcdsg_lib.calendar_functions import get_month, get_month_number
from dsg_lib.calendar_functions import get_month, get_month_number


# Tests for get_month() function
class TestGetMonth(unittest.TestCase):
    def test_valid_input(self):
        # Test with valid input month numbers
        self.assertEqual(get_month(1), "January")
        self.assertEqual(get_month(6), "June")
        self.assertEqual(get_month(12), "December")

    def test_invalid_input(self):
        # Test with invalid input month numbers
        self.assertEqual(get_month(0), "Invalid month number")
        self.assertEqual(get_month(13), "Invalid month number")
        self.assertEqual(get_month(-1), "Invalid month number")

    def test_string_input(self):
        # Test with string input
        self.assertEqual(get_month("January"), "Invalid input, integer is required")
        self.assertEqual(get_month("12"), "Invalid input, integer is required")
        self.assertEqual(get_month("invalid"), "Invalid input, integer is required")

    def test_float_input(self):
        # Test with float input
        self.assertEqual(get_month(3.14), "Invalid input, integer is required")
        self.assertEqual(get_month(8.0), "August")
        self.assertEqual(get_month(12.99), "Invalid input, integer is required")


# Tests for get_month_number() function
class TestGetMonthNumber(unittest.TestCase):
    def test_valid_input(self):
        # Test with valid input month names
        self.assertEqual(get_month_number("January"), 1)
        self.assertEqual(get_month_number("June"), 6)
        self.assertEqual(get_month_number("December"), 12)

    def test_invalid_input(self):
        # Test with invalid input month names
        self.assertEqual(get_month_number("Invalid"), -1)
        self.assertEqual(get_month_number("13"), -1)
        self.assertEqual(get_month_number(""), -1)

    def test_integer_input(self):
        # Test with integer input
        self.assertEqual(get_month_number(1), -1)
        self.assertEqual(get_month_number(6), -1)
        self.assertEqual(get_month_number(12), -1)

    def test_lowercase_input(self):
        # Test with lowercase input
        self.assertEqual(get_month_number("january"), 1)
        self.assertEqual(get_month_number("june"), 6)
        self.assertEqual(get_month_number("december"), 12)

    def test_spaced_input(self):
        # Test with input containing leading/trailing spaces
        self.assertEqual(get_month_number(" January "), 1)
        self.assertEqual(get_month_number("  June   "), 6)
        self.assertEqual(get_month_number(" December  "), 12)

    def test_invalid_type_input(self):
        # Test with invalid type input
        self.assertEqual(get_month_number(None), -1)
        self.assertEqual(get_month_number(3.14), -1)
        self.assertEqual(get_month_number(8), -1)


if __name__ == "__main__":
    unittest.main()

# if __name__ == "__main__":
#     unittest.main()


# class Test(unittest.TestCase):
#     def test_valid_months(self):

#         month_list: list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
#         for i in month_list:
#             result = get_month(month=i)
#             assert result != "Invalid month number"

#     def test_invalid_months(self):

#         month_list: list = [0, 13]
#         for i in month_list:
#             result = get_month(month=i)
#             assert result == "Invalid month number"
