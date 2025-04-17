import logging
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from watchfiles import Change  # Import Change from watchfiles

from dsg_lib.common_functions.file_mover import process_files_flow

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class TestFileMover(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.src_folder = Path(self.test_dir.name) / "src"
        self.temp_folder = Path(self.test_dir.name) / "temp"
        self.dest_folder = Path(self.test_dir.name) / "dest"
        self.src_folder.mkdir()
        self.temp_folder.mkdir()
        self.dest_folder.mkdir()
        self.test_file = self.src_folder / "test.txt"
        self.test_file.write_text("This is a test file.")

    def tearDown(self):
        self.test_dir.cleanup()

    def test_process_files_flow_move_only(self):
        # Test moving a file without compression
        with patch(
            "dsg_lib.common_functions.file_mover.watch",
            return_value=[[(Change.added, str(self.test_file))]],
        ):
            process_files_flow(
                source_dir=str(self.src_folder),
                temp_dir=str(self.temp_folder),
                final_dir=str(self.dest_folder),
                file_pattern="*.txt",
                compress=False,
                max_iterations=1,  # Limit iterations for testing
            )
        self.assertFalse(self.test_file.exists())
        self.assertTrue((self.dest_folder / "test.txt").exists())

    def test_process_files_flow_with_compression(self):
        # Test moving and compressing a file
        with patch(
            "dsg_lib.common_functions.file_mover.watch",
            return_value=iter([[(Change.added, str(self.test_file))]]),
        ):
            process_files_flow(
                source_dir=str(self.src_folder),
                temp_dir=str(self.temp_folder),
                final_dir=str(self.dest_folder),
                file_pattern="*.txt",
                compress=True,
                max_iterations=1,  # Limit iterations for testing
            )
        self.assertFalse(self.test_file.exists())
        compressed_file = next(self.dest_folder.glob("*.zip"), None)
        self.assertIsNotNone(
            compressed_file
        )  # Ensure a compressed file exists in the destination folder

    def test_process_files_flow_invalid_pattern(self):
        # Test with a file that does not match the pattern
        with patch(
            "dsg_lib.common_functions.file_mover.watch",
            return_value=[[(Change.added, str(self.test_file))]],
        ):
            process_files_flow(
                source_dir=str(self.src_folder),
                temp_dir=str(self.temp_folder),
                final_dir=str(self.dest_folder),
                file_pattern="*.log",
                compress=False,
                max_iterations=1,  # Limit iterations for testing
            )
        self.assertTrue(self.test_file.exists())
        self.assertFalse((self.dest_folder / "test.txt").exists())

    def test_process_files_flow_error_handling(self):
        # Test error handling during file processing
        with patch(
            "dsg_lib.common_functions.file_mover.shutil.move",
            side_effect=Exception("Mocked error"),
        ):
            with patch(
                "dsg_lib.common_functions.file_mover.watch",
                return_value=[[(Change.added, str(self.test_file))]],
            ):
                with self.assertRaises(Exception):  # Ensure exception is raised
                    process_files_flow(
                        source_dir=str(self.src_folder),
                        temp_dir=str(self.temp_folder),
                        final_dir=str(self.dest_folder),
                        file_pattern="*.txt",
                        compress=False,
                        max_iterations=1,  # Limit iterations for testing
                    )
        self.assertTrue(self.test_file.exists())

    def test_process_files_flow_compression_error(self):
        # Test error handling during compression
        with patch(
            "dsg_lib.common_functions.file_mover.shutil.make_archive",
            side_effect=Exception("Mocked compression error"),
        ):
            with patch(
                "dsg_lib.common_functions.file_mover.watch",
                return_value=[[(Change.added, str(self.test_file))]],
            ):
                with self.assertRaises(Exception):  # Ensure exception is raised
                    process_files_flow(
                        source_dir=str(self.src_folder),
                        temp_dir=str(self.temp_folder),
                        final_dir=str(self.dest_folder),
                        file_pattern="*.txt",
                        compress=True,
                        max_iterations=1,  # Limit iterations for testing
                    )
        # Verify that the original file remains in the temporary folder
        self.assertTrue((self.temp_folder / "test.txt").exists())
        # Verify that the compressed file does not exist
        self.assertFalse((self.temp_folder / "test.zip").exists())

    def test_process_files_flow_cleanup_error(self):
        # Test error handling during cleanup of uncompressed files
        with patch(
            "dsg_lib.common_functions.file_mover.Path.unlink",
            side_effect=Exception("Mocked cleanup error"),
        ):
            with patch(
                "dsg_lib.common_functions.file_mover.watch",
                return_value=[[(Change.added, str(self.test_file))]],
            ):
                process_files_flow(
                    source_dir=str(self.src_folder),
                    temp_dir=str(self.temp_folder),
                    final_dir=str(self.dest_folder),
                    file_pattern="*.txt",
                    compress=True,
                    max_iterations=1,  # Limit iterations for testing
                )
        # Verify that the compressed file exists in the destination folder
        compressed_file = next(self.dest_folder.glob("*.zip"), None)
        self.assertIsNotNone(compressed_file)  # Ensure a compressed file exists

    def test_process_files_flow_existing_files(self):
        logger.debug("Starting test_process_files_flow_existing_files")
        with patch(
            "dsg_lib.common_functions.file_mover.watch", return_value=iter([[]])
        ):
            process_files_flow(
                source_dir=str(self.src_folder),
                temp_dir=str(self.temp_folder),
                final_dir=str(self.dest_folder),
                file_pattern="*.txt",  # Ensure the pattern matches the test file
                compress=False,
                max_iterations=1,  # Limit iterations for testing
            )
        logger.debug(
            "Finished process_files_flow in test_process_files_flow_existing_files"
        )
        # Verify that the file is moved to the destination directory
        self.assertFalse(self.test_file.exists())
        self.assertTrue((self.dest_folder / "test.txt").exists())

    def test_watch_processing_error_exception(self):
        # Force _process_file to throw an exception during watch processing
        with patch("dsg_lib.common_functions.file_mover.Path.glob", return_value=[]):
            with patch(
                "dsg_lib.common_functions.file_mover._process_file",
                side_effect=Exception("Mocked processing error"),
            ):
                with patch(
                    "dsg_lib.common_functions.file_mover.watch",
                    return_value=iter([[(Change.added, str(self.test_file))]]),
                ):
                    with self.assertRaises(Exception) as context:
                        process_files_flow(
                            source_dir=str(self.src_folder),
                            temp_dir=str(self.temp_folder),
                            final_dir=str(self.dest_folder),
                            file_pattern="*.txt",
                            compress=False,
                            max_iterations=1,  # Limit iterations for testing
                        )
                    self.assertIn("Mocked processing error", str(context.exception))


if __name__ == "__main__":
    unittest.main()
