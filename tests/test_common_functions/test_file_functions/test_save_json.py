# -*- coding: utf-8 -*-

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from dsg_lib.common_functions.file_functions import open_json, save_json


class TestSaveJson(unittest.TestCase):
    def setUp(self) -> None:
        # Define test data
        self.valid_file_name = "test.json"
        self.invalid_file_name = "test/invalid.json"
        self.test_data = {"id": 1, "name": "Test"}

    def test_success_save_json(self):
        # Test successful save of JSON file
        result = save_json(self.valid_file_name, self.test_data)
        self.assertEqual(result, "File saved successfully")
        file_path = Path("data/json") / self.valid_file_name
        self.assertTrue(file_path.exists())

    def test_invalid_file_name(self):
        # Test raise error when file name contains forward slash or backslash
        with self.assertRaises(ValueError):
            save_json(self.invalid_file_name, self.test_data)

    def test_invalid_data_type(self):
        # Test raise error when data is not list or dictionary
        invalid_data = "test"
        with self.assertRaises(TypeError):
            save_json(self.valid_file_name, invalid_data)

    def tearDown(self) -> None:
        # Remove created test files
        file_path = Path("data/json") / self.valid_file_name
        if file_path.exists():
            file_path.unlink()
        # shutil.rmtree(Path("data/json"))


class TestSaveJsonIndentAndEnsureAscii(unittest.TestCase):
    def test_default_output_is_compact_and_ascii_escaped(self):
        # Regression: indent/ensure_ascii are additive -- omitting them must
        # keep json.dump's own defaults (compact, non-ASCII escaped).
        with TemporaryDirectory() as tmp:
            save_json("data.json", {"name": "José"}, root_folder=tmp)
            raw = Path(tmp, "data.json").read_text(encoding="utf-8")
            self.assertNotIn("\n", raw)
            self.assertIn("Jos\\u00e9", raw)

    def test_indent_produces_pretty_printed_output(self):
        with TemporaryDirectory() as tmp:
            save_json("data.json", {"a": 1, "b": {"c": 2}}, root_folder=tmp, indent=2)
            raw = Path(tmp, "data.json").read_text(encoding="utf-8")
            self.assertIn("\n", raw)
            self.assertEqual(json.loads(raw), {"a": 1, "b": {"c": 2}})

    def test_ensure_ascii_false_writes_literal_unicode(self):
        with TemporaryDirectory() as tmp:
            save_json(
                "data.json", {"name": "José"}, root_folder=tmp, ensure_ascii=False
            )
            raw = Path(tmp, "data.json").read_text(encoding="utf-8")
            self.assertIn("José", raw)
            self.assertNotIn("\\u00e9", raw)

    def test_indent_and_ensure_ascii_round_trip_through_open_json(self):
        with TemporaryDirectory() as tmp:
            data = {"name": "José", "nested": {"count": 3}}
            save_json("data.json", data, root_folder=tmp, indent=4, ensure_ascii=False)
            self.assertEqual(open_json("data.json", root_folder=tmp), data)
