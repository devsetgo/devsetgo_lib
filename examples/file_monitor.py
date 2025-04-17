"""
# File Monitor Example

This module demonstrates the usage of the `process_files_flow` function from the `dsg_lib.common_functions.file_mover` library.
It monitors a source directory for files matching a specific pattern, processes them, and moves them to a destination directory,
optionally compressing the files during the process.

## Features

- **Directory Monitoring**: Watches a source directory for files matching a specified pattern (e.g., `*.csv`).
- **File Processing Flow**: Utilizes the `process_files_flow` function to handle file movement and optional compression.
- **Sample File Creation**: Periodically generates sample files in the source directory for testing purposes.
- **Asynchronous Execution**: Leverages Python's `asyncio` for concurrent tasks, such as file creation and processing.

## Configuration

The following constants can be configured to customize the behavior of the script:

- `SOURCE_DIRECTORY`: Path to the directory where files are monitored.
- `TEMPORARY_DIRECTORY`: Path to a temporary directory used during file processing.
- `DESTINATION_DIRECTORY`: Path to the directory where processed files are moved.
- `FILE_PATTERN`: File pattern to monitor (e.g., `*.csv`).
- `COMPRESS_FILES`: Boolean flag to enable or disable file compression during processing.
- `CLEAR_SOURCE`: Boolean flag to clear the source directory before starting.

## Usage

1. Ensure the required directories exist. The script will create them if they do not.
2. Run the script to start monitoring the source directory and processing files.
3. The script will also create sample files in the source directory every 10 seconds for demonstration purposes.

## Example

To run the script:

```bash
python file_monitor.py
```

Press `Ctrl+C` to stop the script.

## Dependencies

- `os` and `pathlib`: For file and directory operations.
- `asyncio`: For asynchronous task management.
- `loguru`: For logging.
- `dsg_lib.common_functions.file_mover`: For the file processing flow.

## Notes

- The script is designed for demonstration purposes and may require adjustments for production use.
- Ensure the `dsg_lib` library is installed and accessible in your environment.

## Error Handling

- The script gracefully handles `KeyboardInterrupt` to stop execution.
- The file creation task is canceled when the main function completes.

## License
This module is licensed under the MIT License.
"""

import asyncio
import os
from pathlib import Path

from loguru import logger

from dsg_lib.common_functions.file_mover import process_files_flow

# Define source, temporary, and destination directories
SOURCE_DIRECTORY: str = "/workspaces/devsetgo_lib/data/move/source/csv"
TEMPORARY_DIRECTORY: str = "/workspaces/devsetgo_lib/data/move/temp"
DESTINATION_DIRECTORY: str = "/workspaces/devsetgo_lib/data/move/destination"
FILE_PATTERN: str = "*.csv"  # File pattern to monitor (e.g., '*.txt')
COMPRESS_FILES: bool = True  # Set to True to compress files before moving
CLEAR_SOURCE: bool = True  # Set to True to clear the source directory before starting

# Ensure directories exist
os.makedirs(SOURCE_DIRECTORY, exist_ok=True)
os.makedirs(TEMPORARY_DIRECTORY, exist_ok=True)
os.makedirs(DESTINATION_DIRECTORY, exist_ok=True)


async def create_sample_files() -> None:
    """
    Periodically create sample files in the source directory for demonstration purposes.

    This coroutine creates a new sample file every 10 seconds in the source directory.
    """
    while True:
        # Count existing files to generate a unique file name
        file_count: int = len(list(Path(SOURCE_DIRECTORY).glob('*')))
        file_name: str = f"sample_{file_count + 1}.txt"
        file_path: Path = Path(SOURCE_DIRECTORY) / file_name
        file_path.write_text("This is a sample file for testing the file mover.")
        logger.info(f"Created sample file: {file_path}")
        await asyncio.sleep(10)  # Create a new file every 10 seconds


async def main() -> None:
    """
    Main function to demonstrate the file mover library.

    Starts the sample file creation task and runs the file processing flow in a separate thread.
    Cancels the file creation task when processing is complete.
    """
    # Start the sample file creation task
    file_creator_task: asyncio.Task = asyncio.create_task(create_sample_files())

    # Run the file processing flow in a separate thread (to avoid blocking the event loop)
    loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    await loop.run_in_executor(
        None,
        process_files_flow,
        SOURCE_DIRECTORY,
        TEMPORARY_DIRECTORY,
        DESTINATION_DIRECTORY,
        FILE_PATTERN,
        COMPRESS_FILES,
        CLEAR_SOURCE,  # Pass the clear_source flag
    )

    # Cancel the file creator task when done
    file_creator_task.cancel()
    try:
        await file_creator_task
    except asyncio.CancelledError:
        logger.info("File creation task cancelled.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("File monitor example stopped.")
