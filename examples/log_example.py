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
    log_rotation='1 MB',
    log_retention='10 days',
    log_backtrace=True,
    log_serializer=False,
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



def log_big_string(_):
    big_string = secrets.token_urlsafe(256)
    for _ in range(100):
        logging.debug(f'Lets make this a big message {big_string}')
        div_zero(x=1, y=0)
        div_zero_two(x=1, y=0)
        # after configuring logging
        # user loguru to log messages
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



def worker():
    for _ in tqdm(range(100), ascii=True):  # Adjusted for demonstration
        log_big_string(None)

def main():
    threads = []
    for _ in range(4):  # Create x threads
        t = threading.Thread(target=worker)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

if __name__ == "__main__":
    main()
