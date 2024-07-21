# -*- coding: utf-8 -*-
"""
Author: Mike Ryan
Date: 2024/05/16
License: MIT
"""
import logging
import secrets
import threading
from loguru import logger
from tqdm import tqdm
from dsg_lib.common_functions import logging_config

# Configure logging as before
logging_config.config_log(
    logging_directory='log',
    log_name='log',
    logging_level='DEBUG',
    log_rotation='100 MB',
    log_retention='10 days',
    log_backtrace=True,
    log_serializer=True,
    log_diagnose=True,
    # app_name='my_app',
    # append_app_name=True,
    file_sink=True,
    intercept_standard_logging=True,
    enqueue=False
)


def div_zero(x, y):
    try:
        return x / y
    except ZeroDivisionError as e:
        logger.error(f'{e}')
        logging.error(f'{e}')


@logger.catch
def div_zero_two(x, y):
    return x / y



def log_big_string(lqty=100, size=256):
    big_string = secrets.token_urlsafe(size)
    for _ in range(lqty):
        logging.debug(f'Lets make this a big message {big_string}')
        div_zero(x=1, y=0)
        div_zero_two(x=1, y=0)
        # after configuring logging
        # use loguru to log messages
        logger.debug('This is a debug message')
        logger.info('This is an info message')
        logger.error('This is an error message')
        logger.warning('This is a warning message')
        logger.critical('This is a critical message')

        # will intercept all standard logging messages also
        logging.debug('This is a debug message')
        logging.info('This is an info message')
        logging.error('This is an error message')
        logging.warning('This is a warning message')
        logging.critical('This is a critical message')


def worker(wqty=100, lqty=100, size=256):
    for _ in tqdm(range(wqty), ascii=True):  # Adjusted for demonstration
        log_big_string(lqty=lqty, size=size)

def main(wqty=100, lqty=100, size=256, workers=2):
    threads = []
    for _ in range(workers):  # Create workers threads
        t = threading.Thread(target=worker, args=(wqty, lqty, size,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

if __name__ == "__main__":
    main(wqty=100, lqty=10, size=256, workers=10)
