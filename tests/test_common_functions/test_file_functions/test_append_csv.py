import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from dsg_lib.common_functions.file_functions import append_csv, open_csv, save_csv


class TestAppendCSV(unittest.TestCase):
    def setUp(self):
        self.test_data = [
            ["Name", "Email"],
            ["John Doe", "jdoe@example.com"],
        ]
        self.append_data = [
            ["Name", "Email"],
            ["Jane Smith", "jsmith@example.com"],
        ]
        self.csv_path = Path("data/csv/test_append.csv")
        if self.csv_path.exists():
            self.csv_path.unlink()

    def tearDown(self):
        if self.csv_path.exists():
            self.csv_path.unlink()

    @patch("dsg_lib.common_functions.file_functions.directory_to_files", "data")
    def test_append_csv_valid_data(self):
        save_csv("test_append", self.test_data)
        result = append_csv("test_append", self.append_data)
        self.assertEqual(result, "appended")
        self.assertTrue(self.csv_path.exists())

    @patch("dsg_lib.common_functions.file_functions.directory_to_files", "data")
    def test_append_csv_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            append_csv("non_existent", self.append_data)

    @patch("dsg_lib.common_functions.file_functions.directory_to_files", "data")
    def test_append_csv_header_mismatch(self):
        save_csv("test_append", self.test_data)
        mismatch_data = [
            ["Different", "Header"],
            ["John Doe", "jdoe@example.com"],
        ]
        with self.assertRaises(ValueError):
            append_csv("test_append", mismatch_data)

    @patch("dsg_lib.common_functions.file_functions.directory_to_files", "data")
    def test_append_csv_invalid_data_type(self):
        save_csv("test_append", self.test_data)
        with self.assertRaises(TypeError):
            append_csv("test_append", "not a list")


class TestAppendCsvColumnsRemap(unittest.TestCase):
    """Covers the `columns` remap option for schema-drifted append data."""

    def test_columns_reorders_rows_to_match_file_header(self):
        with TemporaryDirectory() as tmp:
            save_csv(
                "users.csv", [["name", "email"], ["Jane", "jane@example.com"]],
                root_folder=tmp,
            )
            result = append_csv(
                "users.csv",
                [["joe@example.com", "Joe"]],
                root_folder=tmp,
                columns=["email", "name"],
            )
            self.assertEqual(result, "appended")
            self.assertEqual(
                open_csv("users.csv", root_folder=tmp),
                [
                    {"name": "Jane", "email": "jane@example.com"},
                    {"name": "Joe", "email": "joe@example.com"},
                ],
            )

    def test_columns_already_matching_file_order_still_works(self):
        with TemporaryDirectory() as tmp:
            save_csv(
                "users.csv", [["name", "email"], ["Jane", "jane@example.com"]],
                root_folder=tmp,
            )
            append_csv(
                "users.csv",
                [["Joe", "joe@example.com"]],
                root_folder=tmp,
                columns=["name", "email"],
            )
            self.assertEqual(
                open_csv("users.csv", root_folder=tmp),
                [
                    {"name": "Jane", "email": "jane@example.com"},
                    {"name": "Joe", "email": "joe@example.com"},
                ],
            )

    def test_columns_missing_a_file_column_raises_value_error(self):
        with TemporaryDirectory() as tmp:
            save_csv(
                "users.csv", [["name", "email"], ["Jane", "jane@example.com"]],
                root_folder=tmp,
            )
            with self.assertRaises(ValueError):
                append_csv(
                    "users.csv",
                    [["joe@example.com"]],
                    root_folder=tmp,
                    columns=["email"],
                )

    def test_columns_with_an_extra_unknown_name_raises_value_error(self):
        with TemporaryDirectory() as tmp:
            save_csv(
                "users.csv", [["name", "email"], ["Jane", "jane@example.com"]],
                root_folder=tmp,
            )
            with self.assertRaises(ValueError):
                append_csv(
                    "users.csv",
                    [["joe@example.com", "Joe", "555-1234"]],
                    root_folder=tmp,
                    columns=["email", "name", "phone"],
                )

    def test_without_columns_still_requires_exact_header_match(self):
        # Regression: omitting `columns` must preserve the original
        # exact-header-match behavior.
        with TemporaryDirectory() as tmp:
            save_csv(
                "users.csv", [["name", "email"], ["Jane", "jane@example.com"]],
                root_folder=tmp,
            )
            with self.assertRaises(ValueError):
                append_csv(
                    "users.csv",
                    [["email", "name"], ["joe@example.com", "Joe"]],
                    root_folder=tmp,
                )
