# -*- coding: utf-8 -*-

import os
import secrets
import shutil
import time
import unittest
from pathlib import Path

from dsg_lib.common_functions.file_functions import open_text

random_file_name_for_test = f'test_open_text_{secrets.token_hex(3)}.txt'


class FileFunctionTests(unittest.TestCase):
    directory_to_files = 'data'

    # def setUp(self):
    #     os.makedirs(os.path.join(self.directory_to_files, "text"), exist_ok=True)

    #     # Create test file
    #     with open(
    #         os.path.join(self.directory_to_files, "text", random_file_name_for_test),
    #         "w",
    #         encoding="utf-8",
    #     ) as f:
    #         f.write("<html><body><h1>This is a test</h1></body></html>")
    def setUp(self):
        text_dir = os.path.join(self.directory_to_files, 'text')
        if os.path.exists(text_dir):
            shutil.rmtree(text_dir)
        os.makedirs(text_dir)

        # Create test file
        with open(
            os.path.join(text_dir, random_file_name_for_test),
            'w',
            encoding='utf-8',
        ) as f:
            f.write('<html><body><h1>This is a test</h1></body></html>')

    def tearDown(self):
        test_dir = Path(self.directory_to_files)
        for file_path in test_dir.glob('**/*'):
            if file_path.is_file():
                file_path.unlink()

        # Verify all files have been removed before attempting to remove parent directory
        while os.listdir(os.path.join(self.directory_to_files, 'text')):
            time.sleep(1)
        os.rmdir(os.path.join(self.directory_to_files, 'text'))

    def test_open_text_file(self):
        file_name = random_file_name_for_test
        file_contents = '<html><body><h1>This is a test</h1></body></html>'
        file_path = os.path.join(self.directory_to_files, 'text', file_name)

        # Create test file
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(file_contents)

        # Test function
        result = open_text(file_name)
        self.assertEqual(result, file_contents)

    def test_open_text_invalid_file_name(self):
        invalid_file_name = 'invalid/file/name.txt'

        # Test function
        with self.assertRaises(TypeError):
            open_text(invalid_file_name)

    def test_open_text_nonexistent_file(self):
        nonexistent_file_name = 'nonexistent.txt'

        # Test function
        with self.assertRaises(FileNotFoundError):
            open_text(nonexistent_file_name)

    def test_open_text_integer_file_name(self):
        integer_file_name = 12345

        # Test function
        with self.assertRaises(TypeError):
            open_text(integer_file_name)


if __name__ == '__main__':
    unittest.main()
