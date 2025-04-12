# -*- coding: utf-8 -*-
"""
# Log Example Module

This module demonstrates advanced logging configurations and usage in Python. It integrates both the `logging` module and `loguru` for robust logging capabilities. The module also showcases multi-threading and multi-processing for concurrent execution, while logging messages and handling exceptions.

## Features

- **Logging Configuration**: Configures logging with options for log rotation, retention, backtrace, and serialization.
- **Exception Handling**: Demonstrates exception handling with logging for `ZeroDivisionError`.
- **Concurrent Execution**:
  - Multi-threading: Executes tasks concurrently using threads.
  - Multi-processing: Executes tasks concurrently using processes.
- **Large Message Logging**: Logs large messages repeatedly to test logging performance.
- **Progress Tracking**: Uses `tqdm` to display progress bars for threads and processes.

## Functions

### `div_zero(x, y)`
Attempts to divide `x` by `y` and logs any `ZeroDivisionError` encountered.

### `div_zero_two(x, y)`
Similar to `div_zero`, attempts to divide `x` by `y` and logs any `ZeroDivisionError` encountered.

### `log_big_string(lqty=100, size=256)`
Logs a large string multiple times, demonstrating both standard logging and `loguru` logging.

### `worker(wqty=1000, lqty=100, size=256)`
Executes the `log_big_string` function repeatedly, simulating a worker process or thread.

### `main(wqty, lqty, size, workers, thread_test, process_test)`
Main entry point for the module. Configures and starts either multi-threading or multi-processing based on the provided arguments.

## Usage

Run the module directly to test its functionality. Example:

```bash
python log_example.py
```

You can customize the parameters for workers, logging quantity, and message size by modifying the `main` function call in the `__main__` block.

## Dependencies

- `logging`
- `loguru`
- `multiprocessing`
- `threading`
- `secrets`
- `tqdm`
- `dsg_lib.common_functions`

## Notes

- Ensure the `dsg_lib` library is installed and accessible.
- Adjust the logging configuration as needed for your application.
- Use the `process_test` or `thread_test` flags to toggle between multi-processing and multi-threading.

## License
This module is licensed under the MIT License.
"""
# from loguru import logger
import logging
import logging as logger
import multiprocessing
import secrets
import threading

from tqdm import tqdm

from dsg_lib.common_functions import logging_config

# Configure logging as before
logging_config.config_log(
    logging_directory="log",
    log_name="log",
    logging_level="DEBUG",
    log_rotation="100 MB",
    log_retention="10 days",
    log_backtrace=True,
    log_serializer=True,
    log_diagnose=True,
    # app_name='my_app',
    # append_app_name=True,
    intercept_standard_logging=True,
    enqueue=True,
)


# @logger.catch
def div_zero(x, y):
    try:
        return x / y
    except ZeroDivisionError as e:
        logger.error(f"{e}")
        logging.error(f"{e}")


# @logger.catch
def div_zero_two(x, y):
    try:
        return x / y
    except ZeroDivisionError as e:
        logger.error(f"{e}")
        logging.error(f"{e}")


def log_big_string(lqty=100, size=256):
    big_string = secrets.token_urlsafe(size)
    for _ in range(lqty):
        logging.debug(f"Lets make this a big message {big_string}")
        div_zero(x=1, y=0)
        div_zero_two(x=1, y=0)
        # after configuring logging
        # use loguru to log messages
        logger.debug("This is a loguru debug message")
        logger.info("This is an loguru info message")
        logger.error("This is an loguru error message")
        logger.warning("This is a loguru warning message")
        logger.critical("This is a loguru critical message")

        # will intercept all standard logging messages also
        logging.debug("This is a standard logging debug message")
        logging.info("This is an standard logging info message")
        logging.error("This is an standard logging error message")
        logging.warning("This is a standard logging warning message")
        logging.critical("This is a standard logging critical message")


def worker(wqty=1000, lqty=100, size=256):
    for _ in tqdm(range(wqty), ascii=True, leave=True):  # Adjusted for demonstration
        log_big_string(lqty=lqty, size=size)


def main(
    wqty: int = 100,
    lqty: int = 10,
    size: int = 256,
    workers: int = 16,
    thread_test: bool = False,
    process_test: bool = False,
):
    if process_test:
        processes = []
        # Create worker processes
        for _ in tqdm(range(workers), desc="Multi-Processing Start", leave=True):
            p = multiprocessing.Process(
                target=worker,
                args=(
                    wqty,
                    lqty,
                    size,
                ),
            )
            processes.append(p)
            p.start()

        for p in tqdm((processes), desc="Multi-Processing Start", leave=False):
            p.join(timeout=60)  # Timeout after 60 seconds
            if p.is_alive():
                logger.error(f"Process {p.name} is hanging. Terminating.")
                p.terminate()
                p.join()

    if thread_test:
        threads = []
        for _ in tqdm(
            range(workers), desc="Threading Start", leave=True
        ):  # Create worker threads
            t = threading.Thread(
                target=worker,
                args=(
                    wqty,
                    lqty,
                    size,
                ),
            )
            threads.append(t)
            t.start()

        for t in tqdm(threads, desc="Threading Gather", leave=False):
            t.join()


if __name__ == "__main__":
    from time import time

    start = time()
    main(wqty=5, lqty=50, size=64, workers=8, thread_test=False, process_test=True)
    print(f"Execution time: {time()-start:.2f} seconds")
