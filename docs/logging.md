# Logging Configuration
This module uses [Loguru](https://loguru.readthedocs.io/) 0.5.0 or higher to manage logging. The module will intercept standard logging and add to logging file.


### TODO:
- none


### Configuration

Simple zero config
~~~python
from dsg_liblogging_config import config_log
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
from devsetgo_lib import logging_config
from loguru import logger
import logging


logging_config.config_log(
    logging_directory="myLoggingFolder",
    # or None and defaults to logging
    log_name="mylog.log",
    # or None and defaults to "log.log"
    logging_level="debug",
    # or "info" or "debug" or "warning" or "error" or "critical" or None and defaults to "info"
    log_rotation="1 MB",
    # or None and default is 10 MB
    log_retention="1 Day",
    # or None and defaults to "14 Days"
    log_backtrace=True,
    # or None and defaults to False
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
~~~


## Using FastAPI
Zero config example. Should run as is. Requires

~~~python
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
import logging

from loguru import logger

from dsg_lib import logging_config

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