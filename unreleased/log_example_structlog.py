# -*- coding: utf-8 -*-
"""
Author: Mike Ryan
Date: 2024/05/16
License: MIT
"""
import logging
import multiprocessing
import secrets
import threading

import structlog
from tqdm import tqdm

from dsg_lib.common_functions import logging_config_structlog


logger = structlog.get_logger()


def div_zero(x, y):
    try:
        return x / y
    except ZeroDivisionError as e:
        logger.error("division by zero", error=str(e))
        logging.error(f'{e}')


def div_zero_two(x, y):
    try:
        return x / y
    except ZeroDivisionError as e:
        logger.error("division by zero", error=str(e))
        logging.error(f'{e}')


def log_big_string(lqty=100, size=256):
    # big_string = secrets.token_urlsafe(size)
    big_string = """
    Bacon ipsum dolor amet meatball kielbasa chislic, corned beef ham hock frankfurter jowl sirloin meatloaf ribeye boudin. Capicola ham hock pork landjaeger, jerky t-bone strip steak pork chop boudin shankle tri-tip andouille pork belly flank.
    """
    for _ in range(lqty):
        logging.debug(f'Lets make this a big message {big_string}')
        div_zero(x=1, y=0)
        div_zero_two(x=1, y=0)
        logger.debug('This is a debug message')
        logger.info('This is an info message')
        logger.error('This is an error message')
        logger.warning('This is a warning message')
        logger.critical('This is a critical message')

        logging.debug('This is a debug message')
        logging.info('This is an info message')
        logging.error('This is an error message')
        logging.warning('This is a warning message')
        logging.critical('This is a critical message')


def worker(wqty=1000, lqty=100, size=256):
    for _ in tqdm(range(wqty), desc="Worker", leave=True, ascii=True):  # Adjusted for demonstration
        log_big_string(lqty=lqty, size=size)


def main(wqty: int = 100, lqty: int = 10, size: int = 256, workers: int = 16, thread_test: bool = False, process_test: bool = False):
    if process_test:
        processes = []
        # Create worker processes
        for _ in tqdm(range(workers), desc="Multi-Processing Start", leave=True):
            p = multiprocessing.Process(
                target=worker, args=(wqty, lqty, size,))
            processes.append(p)
            p.start()

        for p in tqdm((processes), desc="Multi-Processing Start", leave=True):
            p.join(timeout=60)  # Timeout after 60 seconds
            if p.is_alive():
                logger.error(f"Process {p.name} is hanging. Terminating.")
                p.terminate()
                p.join()

    if thread_test:
        threads = []
        for _ in tqdm(range(workers), desc="Threading Start", leave=True):  # Create worker threads
            t = threading.Thread(target=worker, args=(wqty, lqty, size,))
            threads.append(t)
            t.start()

        for t in tqdm(threads, desc="Threading Gather", leave=True):
            t.join()


if __name__ == "__main__":
    logging_config_structlog.configure_logging(
        logging_directory='log',
        log_name='log',
        logging_level='INFO',
        log_rotation=100,  # Size in MB
        log_retention=10
    )
    from time import time
    start = time()
    main(wqty=100, lqty=100, size=256, workers=16,
         thread_test=True, process_test=True)
    print(f"Execution time: {time()-start:.2f} seconds")
