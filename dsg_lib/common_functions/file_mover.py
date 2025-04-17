#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module: file_mover
Detailed file processing flow that continuously monitors and processes files
from a source directory, optionally compresses them, and then moves them to a
final destination. Ensures no files are lost during transfer.

Functions:
    process_files_flow(
        source_dir: str,
        temp_dir: str,
        final_dir: str,
        file_pattern: str,
        compress: bool = False,
        max_iterations: Optional[int] = None
    ) -> None:
        Continuously monitors the source directory for files matching the given
        pattern, moves them to a temporary directory, optionally compresses them,
        and then transfers them to the final directory.

    _process_file(file_path: Path, temp_path: Path, final_path: Path, compress: bool) -> None:
        Handles the internal logic of moving and optionally compressing a single file.

Usage Example:
```python
from dsg_lib.common_functions.file_mover import process_files_flow

process_files_flow(
    source_dir="/some/source",
    temp_dir="/some/temp",
    final_dir="/some/final",
    file_pattern="*.txt",
    compress=True
)
```
"""

import shutil
from datetime import datetime
from itertools import islice  # Import islice to limit generator iterations
from pathlib import Path
from time import sleep
from typing import Optional, Generator, Set, Tuple

from loguru import logger
from watchfiles import watch


def process_files_flow(
    source_dir: str,
    temp_dir: str,
    final_dir: str,
    file_pattern: str,
    compress: bool = False,
    max_iterations: Optional[int] = None,
) -> None:
    """
    Continuously monitors a source directory for files. Moves files matching
    file_pattern to a temporary directory, optionally compresses them, then
    moves them to a final destination directory.

    Args:
        source_dir (str): Path to the source directory to watch.
        temp_dir (str): Path to the temporary directory for processing.
        final_dir (str): Path to the final destination directory.
        file_pattern (str): Glob pattern for matching files (e.g. "*.txt").
        compress (bool, optional): If True, compress files before moving. Defaults to False.
        max_iterations (Optional[int], optional): Limit iterations in watch loop. Defaults to None.

    Returns:
        None

    Raises:
        Exception: Propagated if file operations fail.

    Example:
        process_files_flow("/source", "/temp", "/final", "*.pdf", compress=True)
    """
    temp_path: Path = Path(temp_dir)
    final_path: Path = Path(final_dir)
    source_path: Path = Path(source_dir)

    # Ensure temporary and final directories exist.
    for path in (temp_path, final_path):
        path.mkdir(parents=True, exist_ok=True)

    # Process existing files in the source directory at startup
    logger.info(f"Processing existing files in source directory: {source_dir}")
    for file in source_path.glob(file_pattern):
        if file.is_file():
            try:
                logger.info(f"Processing existing file: {file}")
                _process_file(file, temp_path, final_path, compress)
            except Exception as e:
                logger.error(f"Error processing existing file '{file}': {e}")
                raise

    # The clear_source deletion block has been removed so that files remain in the source directory
    # if they have not already been processed.

    logger.info(
        f"Starting file processing flow: monitoring '{source_dir}' for pattern '{file_pattern}'."
    )

    # Monitor the source directory for changes
    changes_generator: Generator[Set[Tuple[int, str]], None, None] = watch(source_dir)
    if max_iterations is not None:
        changes_generator = islice(changes_generator, max_iterations)

    for changes in changes_generator:
        logger.debug(f"Detected changes: {changes}")
        for _change_type, file_str in changes:
            file_path: Path = Path(file_str)
            # Only process files matching the pattern and that are files
            if file_path.is_file() and file_path.match(file_pattern):
                try:
                    logger.info(f"Detected file for processing: {file_path}")
                    _process_file(file_path, temp_path, final_path, compress)
                except Exception as e:
                    logger.error(f"Error processing file '{file_path}': {e}")
                    raise
        sleep(1)  # Small delay to minimize CPU usage


def _process_file(
    file_path: Path, temp_path: Path, final_path: Path, compress: bool
) -> None:
    """
    Handles the internal logic of relocating and optionally compressing a single file.

    Args:
        file_path (Path): Full path to the file being processed.
        temp_path (Path): Temporary directory path.
        final_path (Path): Final destination directory path.
        compress (bool): Flag indicating whether to compress the file.

    Returns:
        None

    Raises:
        Exception: Raised if errors occur during file move or compression steps.
    """
    logger.debug(f"Starting to process file: {file_path}")
    # Step 1: Move the file to the temporary directory
    temp_file_path: Path = temp_path / file_path.name
    logger.debug(f"Attempting to move file to temporary directory: {temp_file_path}")
    shutil.move(str(file_path), str(temp_file_path))
    logger.info(f"Moved file to temporary directory: {temp_file_path}")

    processed_file_path: Path = temp_file_path

    # Step 2: Optionally compress the file
    if compress:
        try:
            logger.debug(f"Starting compression for file: {temp_file_path}")
            # Add a timestamp to the zip file name to avoid collisions
            timestamp_suffix: str = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            base_for_zip: Path = (
                temp_file_path.parent / f"{temp_file_path.stem}_{timestamp_suffix}"
            )
            shutil.make_archive(
                base_name=str(base_for_zip),
                format="zip",
                root_dir=temp_file_path.parent,
                base_dir=temp_file_path.name,
            )
            zipped_file: Path = base_for_zip.with_suffix(".zip")
            logger.info(f"Compressed file to: {zipped_file}")
            processed_file_path = zipped_file

            # Attempt to remove the uncompressed file
            try:
                logger.debug(
                    f"Attempting to delete uncompressed file: {temp_file_path}"
                )
                temp_file_path.unlink()
                logger.info(f"Deleted uncompressed file: {temp_file_path}")
            except Exception as cleanup_err:
                logger.error(
                    f"Error deleting temporary file {temp_file_path}: {cleanup_err}"
                )

        except Exception as compression_err:
            logger.error(f"Error compressing file {temp_file_path}: {compression_err}")
            raise

    # Step 3: Move the (processed) file to the final directory
    final_file_path: Path = final_path / processed_file_path.name
    logger.debug(
        f"Attempting to move processed file to final directory: {final_file_path}"
    )
    shutil.move(str(processed_file_path), str(final_file_path))
    logger.info(f"Moved file to final destination: {final_file_path}")


if __name__ == "__main__":
    SOURCE_DIRECTORY: str = "/path/to/source"
    TEMPORARY_DIRECTORY: str = "/path/to/temp"
    FINAL_DIRECTORY: str = "/path/to/final"
    FILE_PATTERN: str = "*.txt"
    COMPRESS_FILE: bool = True

    process_files_flow(
        SOURCE_DIRECTORY,
        TEMPORARY_DIRECTORY,
        FINAL_DIRECTORY,
        FILE_PATTERN,
        COMPRESS_FILE,
    )
