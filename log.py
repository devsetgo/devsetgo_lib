import loguru
from devsetgo_lib import logging_config

logging_config.config_log(
    logging_directory="logging", # or None
    log_name="log.log", # or None
    logging_level="debug", # or "info" or "debug" or "warning" or "error" or "critical"
    log_rotation="1 MB", # or None and default is 10 MB
    log_retention="1 Day", # or None and defaults to "14 Days"
    log_backtrace=True, # or None and defaults to False
)

# after configuring logging
# user loguru to log messages
from loguru import logger
logger.debug("This is a debug message")
logger.info("This is an info message")
logger.error("This is an error message")
logger.warning("This is a warning message")
logger.critical("This is a critical message")

# will intercept all standard logging messages also
import logging
logging.debug("This is a debug message")
logging.info("This is an info message")
logging.error("This is an error message")
logging.warning("This is a warning message")
logging.critical("This is a critical message")


def div_zero(x, y):
    try:
        result = x / y
    except ZeroDivisionError as e:
        logger.error(f"{e}")

@logger.catch
def div_zero(x, y):
    return x / y

div_zero(x=1, y=0)