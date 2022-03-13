# Logging Configuration
This module uses [Loguru](https://loguru.readthedocs.io/) 0.6.0 or higher to manage logging. The module will intercept standard logging and add to logging file.


### TODO:
- none


### Configuration

Simple zero config
~~~python
from dsg_lib.logging_config import config_log
from loguru import logger
import logging
# no configuration necessary as all have default values that are secure.
config_log()
# after configuring logging
# user loguru to log messages
logger.debug("This is a debug message")
logger.info("This is an info message")
logger.error("This is an error message")
logger.warning("This is a warning message")
logger.critical("This is a critical message")

# will intercept all standard logging messages also
logging.debug("This is a debug message")
logging.info("This is an info message")
logging.error("This is an error message")
logging.warning("This is a warning message")
logging.critical("This is a critical message")
~~~

Configuration settings

~~~python
# -*- coding: utf-8 -*-
import logging
import secrets
from uuid import uuid4
from loguru import logger
from tqdm import tqdm
from dsg_lib import logging_config

logging_config.config_log(
    logging_directory="log",
    # or None and defaults to logging
    log_name="log.log",
    # or None and defaults to "log.log"
    logging_level="debug",
    # or "info" or "debug" or "warning" or "error" or "critical"
    # or None and defaults to "info"
    log_rotation="10 MB",
    # or None and default is 10 MB
    log_retention="1 Day",
    # or None and defaults to "14 Days"
    log_backtrace=True,
    # or None and defaults to False
    app_name="my_app",
    # app name is used to identify the application
    # this is an optional field
    service_id=uuid4(),
    # service id is used to identify the service
    # this is an optional field
    append_app_name=True,
    # append app name to log file name defaults to false
    append_service_id=True,
    # append app name and service name to log file name defaults to false
)

# after configuring logging
# user loguru to log messages
logger.debug("This is a debug message")
logger.info("This is an info message")
logger.error("This is an error message")
logger.warning("This is a warning message")
logger.critical("This is a critical message")

# will intercept all standard logging messages also
logging.debug("This is a debug message")
logging.info("This is an info message")
logging.error("This is an error message")
logging.warning("This is a warning message")
logging.critical("This is a critical message")


def div_zero(x, y):

    try:
        return x / y
    except ZeroDivisionError as e:
        logger.error(f"{e}")
        logging.error(f"{e}")


@logger.catch
def div_zero_two(x, y):
    return x / y


a = div_zero(x=1, y=0)
b = div_zero_two(x=1, y=0)

for _ in tqdm(range(5), ascii=True):
    # log a lot of data
    logging.debug(f"Lets make this a big message {secrets.token_urlsafe(32)}")

~~~


## Using FastAPI
Zero config example. Should run as is. Requires

~~~python
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
import logging

from loguru import logger

from dsg_lib. import logging_config

logging_config.config_log()

app = FastAPI()


@app.get("/")
async def root():
    """
    Root endpoint of API
    Returns:
        Redrects to openapi document
    """
    # redirect to openapi docs
    logger.info("Redirecting to OpenAPI docs")
    response = RedirectResponse(url="/docs")
    return response


~~~