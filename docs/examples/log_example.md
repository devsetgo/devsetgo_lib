# log_example Example

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

```python
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


def div_zero(x: float, y: float) -> float | None:
    """
    Safely divide x by y and log ZeroDivisionError if encountered.

    Args:
        x (float): Numerator.
        y (float): Denominator.
    Returns:
        float | None: Quotient or None on error.
    """
    try:
        return x / y
    except ZeroDivisionError as e:
        logger.error(f"{e}")       # log via loguru
        logging.error(f"{e}")      # log via standard logging


def div_zero_two(x: float, y: float) -> float | None:
    """
    Mirror of div_zero demonstrating identical error handling.
    """
    try:
        return x / y
    except ZeroDivisionError as e:
        logger.error(f"{e}")
        logging.error(f"{e}")


def log_big_string(lqty: int = 100, size: int = 256) -> None:
    """
    Generate a large random string and log various messages repeatedly.

    Args:
        lqty (int): Number of log iterations.
        size (int): Length of each random string.
    """
    big_string = secrets.token_urlsafe(size)  # create URL-safe token
    for _ in range(lqty):
        logging.debug(f"Lets make this a big message {big_string}")  # standard debug
        div_zero(1, 0)     # trigger/log ZeroDivisionError
        div_zero_two(1, 0)
        # loguru messages
        logger.debug("This is a loguru debug message")
        logger.info("This is a loguru info message")
        logger.warning("This is a loguru warning message")
        logger.error("This is a loguru error message")
        logger.critical("This is a loguru critical message")
        # continued standard logging
        logging.info("This is a standard logging info message")
        logging.warning("This is a standard logging warning message")
        logging.error("This is a standard logging error message")
        logging.critical("This is a standard logging critical message")


def worker(wqty: int = 1000, lqty: int = 100, size: int = 256) -> None:
    """
    Worker routine performing log_big_string in a progress loop.

    Args:
        wqty (int): Number of outer iterations.
        lqty (int): Messages per iteration.
        size (int): Random string length.
    """
    for _ in tqdm(range(wqty), ascii=True, leave=True):
        log_big_string(lqty=lqty, size=size)


def main(
    wqty: int = 100,
    lqty: int = 10,
    size: int = 256,
    workers: int = 16,
    thread_test: bool = False,
    process_test: bool = False,
) -> None:
    """
    Configure and launch concurrent logging workers.

    Args:
        wqty (int): Iterations per worker.
        lqty (int): Logs per iteration.
        size (int): Random string size.
        workers (int): Thread/process count.
        thread_test (bool): Run threads if True.
        process_test (bool): Run processes if True.
    """
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
```
