# -*- coding: utf-8 -*-
"""
Author: Mike Ryan
Date: 2024/05/16
License: MIT
"""
import logging
import random
import secrets

from loguru import logger
from tqdm import tqdm

from dsg_lib.common_functions import logging_config

logging_config.config_log(
    logging_directory='log',  # Directory where logs will be stored
    log_name='log',  # Name of the log file
    logging_level='DEBUG',  # Logging level
    log_rotation='500 MB',  # Log rotation size
    log_retention='10 days',  # Log retention period
    log_backtrace=True,  # Enable backtrace
    # log_format="<green>{time:YYYY-MM-DD HH:mm:ss.SSSSSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",  # Log format
    log_serializer=False,  # Disable log serialization
    log_diagnose=True,  # Enable diagnose
    app_name='my_app',  # Application name
    append_app_name=True,  # Append application name to the log file name
)

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


def div_zero(x, y):
    try:
        return x / y
    except ZeroDivisionError as e:
        logger.error(f'{e}')
        logging.error(f'{e}')


@logger.catch
def div_zero_two(x, y):
    return x / y


a = div_zero(x=1, y=0)
b = div_zero_two(x=1, y=0)

for _ in tqdm(range(5000), ascii=True):
    big_string = ''
    for _ in range(random.randint(275, 1000)):
        big_string += f'{secrets.token_urlsafe(random.randint(1,5))} '
    # log a lot of data
    logging.debug(f'Lets make this a big message {big_string}')
