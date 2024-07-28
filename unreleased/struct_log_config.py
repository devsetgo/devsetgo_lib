# -*- coding: utf-8 -*-
"""
Simplification and standardization of structlog configuration for Python applications. This module provides a basic configuration for structlog, a powerful logging library that supports structured logging. The `config_log` function sets up a logger with a console sink and a file sink, and allows for customization of the logging level, log file name, and log format. It also provides a `get_logger` function to retrieve the configured logger.

Author: Mike Ryan
DateCreated: 2021/07/21
DateUpdated: 2024/07/21

License: MIT
"""
import logging
import logging.handlers
import os
import zipfile
from logging.handlers import BaseRotatingHandler
import time
from datetime import datetime
import structlog
import colorama

# Initialize colorama for ANSI color codes
colorama.init()

class TimedRotatingFileHandlerWithZip(BaseRotatingHandler):
    def __init__(self, filename, when='midnight', interval=1, backupCount=5, maxBytes=100*1024*1024, encoding=None, delay=False, utc=False):
        self.when = when.upper()
        self.backupCount = backupCount
        self.maxBytes = maxBytes
        self.utc = utc
        self.interval = self.compute_interval(when, interval)
        self.suffix = "%Y-%m-%d"
        self.extMatch = r"^\d{4}-\d{2}-\d{2}$"
        BaseRotatingHandler.__init__(self, filename, 'a', encoding, delay)
        self.rolloverAt = self.compute_rollover(time.time())

    def compute_interval(self, when, interval):
        when_upper = when.upper()
        if when_upper == 'MIDNIGHT':
            return 86400 * interval  # 86400 seconds in a day
        else:
            supported_intervals = ['MIDNIGHT']  # Extend this list as needed
            raise ValueError(f"Invalid rollover interval specified: {when}. Supported intervals are: {', '.join(supported_intervals)}")

    def compute_rollover(self, currentTime):
        if self.when == 'MIDNIGHT':
            if self.utc:
                t = time.gmtime(currentTime)
            else:
                t = time.localtime(currentTime)
            currentDay = time.mktime(t[:3] + (0, 0, 0) + t[6:9])
            return currentDay + self.interval
        else:
            return currentTime + self.interval

    def shouldRollover(self, record):
        if self.stream.tell() + len(self.format(record)) >= self.maxBytes:
            return 1
        currentTime = int(time.time())
        if currentTime >= self.rolloverAt:
            return 1
        return 0

    def doRollover(self):
        self.stream.close()
        if self.backupCount > 0:
            for i in range(self.backupCount - 1, 0, -1):
                sfn = self.rotation_filename("%s.%s" % (self.baseFilename, self.timeSuffix(i)))
                dfn = self.rotation_filename("%s.%s.zip" % (self.baseFilename, self.timeSuffix(i + 1)))
                if os.path.exists(sfn):
                    with zipfile.ZipFile(dfn, 'w', zipfile.ZIP_DEFLATED) as zf:
                        zf.write(sfn, os.path.basename(sfn))
                    os.remove(sfn)
        dfn = self.rotation_filename("%s.%s.zip" % (self.baseFilename, self.timeSuffix(0)))
        if os.path.exists(dfn):
            os.remove(dfn)
        self.rotate(self.baseFilename, dfn)
        if not self.delay:
            self.stream = self._open()
        currentTime = int(time.time())
        newRolloverAt = self.compute_rollover(currentTime)
        while newRolloverAt <= currentTime:
            newRolloverAt += self.interval
        self.rolloverAt = newRolloverAt

    def rotate(self, source, dest):
        with zipfile.ZipFile(dest, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.write(source, os.path.basename(source))
        os.remove(source)

    def timeSuffix(self, idx):
        timeTuple = time.localtime(time.time() - (self.interval * idx))
        return time.strftime(self.suffix, timeTuple)

def custom_log_processor(logger, method_name, event_dict):
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    level = event_dict.get('level', '').upper()
    name = event_dict.get('logger_name', '')
    function = event_dict.get('function', '')
    line = event_dict.get('line', '')
    message = event_dict.get('event', '')
    formatted_message = (
        f"{colorama.Fore.GREEN}{timestamp}{colorama.Style.RESET_ALL} | "
        f"{level: <8} | "
        f"{colorama.Fore.CYAN}{name}{colorama.Style.RESET_ALL}:"
        f"{colorama.Fore.CYAN}{function}{colorama.Style.RESET_ALL}:"
        f"{colorama.Fore.CYAN}{line}{colorama.Style.RESET_ALL} - "
        f"{message}"
    )
    return formatted_message

def configure_structlog(log_filename:str='~/log/app.log', level:str='INFO'):
    handler = TimedRotatingFileHandlerWithZip(log_filename, when="midnight", interval=1, backupCount=5)
    logging.basicConfig(handlers=[handler], level=level.upper())
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            custom_log_processor,  # Use the custom processor
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

# Example usage
if __name__ == "__main__":
    configure_structlog(log_filename='/workspaces/devsetgo_lib/log/app.log',level='DEBUG')
    logger = structlog.get_logger(__name__)
    logger.info("This is a test log message", function="main", line=75)
    logger.debug("This is a debug message", function="main", line=76)
