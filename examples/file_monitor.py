import os
import asyncio
from pathlib import Path
from loguru import logger
from dsg_lib.common_functions.file_mover import process_files_flow

# Define source, temporary, and destination directories
SOURCE_DIRECTORY = "/workspaces/devsetgo_lib/data/move/source/csv"
TEMPORARY_DIRECTORY = "/workspaces/devsetgo_lib/data/move/temp"
DESTINATION_DIRECTORY = "/workspaces/devsetgo_lib/data/move/destination"
FILE_PATTERN = "*.csv"  # File pattern to monitor (e.g., '*.txt')
COMPRESS_FILES = True  # Set to True to compress files before moving
CLEAR_SOURCE = True  # Set to True to clear the source directory before starting

# Ensure directories exist
os.makedirs(SOURCE_DIRECTORY, exist_ok=True)
os.makedirs(TEMPORARY_DIRECTORY, exist_ok=True)
os.makedirs(DESTINATION_DIRECTORY, exist_ok=True)


async def create_sample_files():
    """
    Periodically create sample files in the source directory for demonstration purposes.
    """
    while True:
        file_name = f"sample_{Path(SOURCE_DIRECTORY).glob('*').__len__() + 1}.txt"
        file_path = Path(SOURCE_DIRECTORY) / file_name
        file_path.write_text("This is a sample file for testing the file mover.")
        logger.info(f"Created sample file: {file_path}")
        await asyncio.sleep(10)  # Create a new file every 10 seconds


async def main():
    """
    Main function to demonstrate the file mover library.
    """
    # Start the sample file creation task
    file_creator_task = asyncio.create_task(create_sample_files())

    # Run the file processing flow in a separate thread
    loop = asyncio.get_event_loop()
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
