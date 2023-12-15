# -*- coding: utf-8 -*-
import os
import unittest

from dsg_lib.functions.file_functions import create_sample_files


class TestSampleGenerator(unittest.TestCase):
    def setUp(self) -> None:
        self.sample_size = 10
        self.file_name = "test_file_create_sample_data"
        self.csv_file = f"data/csv/{self.file_name}.csv"
        self.json_file = f"data/json/{self.file_name}.json"

    # def tearDown(self) -> None:
    #     os.remove(self.csv_file)
    #     os.remove(self.json_file)

    def test_files_created_successfully(self) -> None:
        # Create the sample files
        create_sample_files(self.file_name, self.sample_size)

        # Print the CSV file path for troubleshooting
        print(f"CSV file path: {self.csv_file}")

        # Check if the CSV file was created successfully
        self.assertTrue(os.path.exists(self.csv_file))

        # Print the JSON file path for troubleshooting
        print(f"JSON file path: {self.json_file}")

        # Check if the JSON file was created successfully
        self.assertTrue(os.path.exists(self.json_file))


if __name__ == "__main__":
    unittest.main()
