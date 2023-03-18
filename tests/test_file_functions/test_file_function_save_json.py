import unittest
from unittest.mock import patch
from tempfile import TemporaryDirectory
from dsg_lib.file_functions import save_json
from pathlib import Path

class TestSaveJson(unittest.TestCase):
    def setUp(self):
        self.tmpdir = TemporaryDirectory()
        self.datadir = Path(self.tmpdir.name) / 'data'
        self.datadir.mkdir()
        self.csvdir = self.datadir / 'csv'
        self.csvdir.mkdir()
        self.jsondir = self.datadir / 'json'
        self.jsondir.mkdir()
        self.textdir = self.datadir / 'text'
        self.textdir.mkdir()

        # Create some test files
        self.csvfile = self.csvdir / 'test.csv'
        self.csvfile.touch()
        self.jsonfile = self.jsondir / 'test.json'
        self.jsonfile.touch()
        self.textfile = self.textdir / 'test.txt'
        self.textfile.touch()

    def tearDown(self):
        self.temp_dir.cleanup()

    @patch("dsg_lib.file_functions.directory_to_files", "data")
    def test_save_json_valid_data(self):
        # Test saving a JSON file with valid data
        data = {"name": "John Doe", "age": 42}
        file_name = "test.json"

        with patch("dsg_lib.file_functions.os.makedirs") as mock_makedirs:
            with patch("dsg_lib.file_functions.open") as mock_open:
                save_json(file_name, data, root_folder=self.root_folder)

                # Check that the file was written to the correct location
                mock_makedirs.assert_called_once_with(f"{self.root_folder}/json", exist_ok=True)
                mock_open.assert_called_once_with(f"{self.root_folder}/json/{file_name}", "w+")

    def test_save_json_invalid_data(self):
        # Test saving a JSON file with invalid data
        data = "invalid data"
        file_name = "test.json"

        with self.assertRaises(TypeError):
            save_json(file_name, data, root_folder=self.root_folder)

    def test_save_json_invalid_filename(self):
        # Test saving a JSON file with an invalid filename
        data = {"name": "John Doe", "age": 42}
        file_name = "invalid/filename.json"

        with self.assertRaises(ValueError):
            save_json(file_name, data, root_folder=self.root_folder)