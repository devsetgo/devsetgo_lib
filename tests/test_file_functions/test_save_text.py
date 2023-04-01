import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from dsg_lib.file_functions import save_text


class SaveTextTestCase(unittest.TestCase):
    def setUp(self):
        """Create a temporary directory for the test files"""
        self.temp_dir = TemporaryDirectory()
        self.data_dir = os.path.join(self.temp_dir.name, "data")
        os.makedirs(self.data_dir)

    def tearDown(self):
        """Delete the temporary directory and its contents"""
        self.temp_dir.cleanup()

    @patch("dsg_lib.file_functions.save_text", side_effect=save_text)
    def test_save_text(self, mock_save_text):
        """Test that text is saved to a file"""
        # Create text to save to file
        text = "Hello, world!"

        # Save text to file
        file_name = "test_file"
        mock_save_text(file_name=file_name, data=text, root_folder=self.data_dir)

        # Check that file was created and contains the correct text
        file_path = os.path.join(self.data_dir, "text", f"{file_name}.txt")
        self.assertTrue(os.path.exists(file_path))
        with open(file_path, "r") as file:
            self.assertEqual(file.read(), text)

    @patch("dsg_lib.file_functions.save_text", side_effect=save_text)
    def test_save_text_invalid_data(self, mock_save_text):
        """Test that an exception is raised when the data parameter is not a string"""
        # Try to save a non-string value to a file
        file_name = "test_file"
        invalid_data = 123
        with self.assertRaises(TypeError):
            mock_save_text(
                file_name=file_name, data=invalid_data, root_folder=self.data_dir
            )

    @patch("dsg_lib.file_functions.save_text", side_effect=save_text)
    def test_save_text_invalid_file_name(self, mock_save_text):
        """Test that an exception is raised when the file name parameter contains a forward slash or backslash"""
        # Try to save a file with an invalid file name
        file_name = "invalid/file/name"
        text = "This should not be saved to a file"
        with self.assertRaises(ValueError):
            mock_save_text(file_name=file_name, data=text, root_folder=self.data_dir)
