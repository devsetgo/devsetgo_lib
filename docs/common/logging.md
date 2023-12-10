# Logging Configuration
This module uses [Loguru](https://loguru.readthedocs.io/) 0.6.0 or higher to manage logging.

===================================================
### TODO:
- none
===================================================

===================================================
## Introduction to Logging Config:
===================================================
The `dsg_lib.logging_config` library code provides a configuration and interceptor for standard python logging using the `loguru` package. This library allows developers to customize logging options and create a more efficient logging system. This user documentation explains the configuration options and how to use the library code.

===================================================
### Usage:

To use the `dsg_lib.logging_config` library code, first, you need to import it in your Python script as follows:

```python
from dsg_lib.logging_config import config_log
```

Then, you can call the `config_log()` function with the desired parameters to configure the logging system. The following parameters are available:

- logging_directory: str = "log",  # directory where log file will be stored
- log_name: str = "log.json",  # name of the log file
- logging_level: str = "INFO",  # level of logging
- log_rotation: str = "10 MB",  # size at which log file should be rotated
- log_retention: str = "30 days",  # how long logging data should be retained
- log_backtrace: bool = False,  # whether backtraces should be logged
- log_format: str = "'time': '{time:YYYY-MM-DD HH:mm:ss.SSSSSS}', 'level': '{level: <8}', 'name': '{name}', 'function': '{function}', 'line': '{line}', 'message': '{message}',",  # format of log messages
- log_serializer: bool = True,  # whether the log should be serialized
- log_diagnose: bool = False,  # whether to show logging diagnostics
- app_name: str = None,  # name of the application being logged
- append_app_name: bool = False,  # whether to append the application name to the log file name
- append_trace_id: bool = False,  # whether to append a trace ID to the log file name
- enable_trace_id: bool = False,  # whether to enable tracing for the log file


===================================================
### Example:

Below is the base configuration and can be called with just `config_log()`

```python
from dsg_lib.logging_config import config_log

config_log(
    logging_directory: str = "log",  # directory where log file will be stored
    log_name: str = "log.json",  # name of the log file
    logging_level: str = "INFO",  # level of logging
    log_rotation: str = "10 MB",  # size at which log file should be rotated
    log_retention: str = "30 days",  # how long logging data should be retained
    log_backtrace: bool = False,  # whether backtraces should be logged
    log_format: str = "'time': '{time:YYYY-MM-DD HH:mm:ss.SSSSSS}', 'level': '{level: <8}', 'name': '{name}', 'function': '{function}', 'line': '{line}', 'message': '{message}',",  # format of log messages
    log_serializer: bool = True,  # whether the log should be serialized
    log_diagnose: bool = False,  # whether to show logging diagnostics
    app_name: str = None,  # name of the application being logged
    append_app_name: bool = False,  # whether to append the application name to the log file name
    append_trace_id: bool = False,  # whether to append a trace ID to the log file name
    enable_trace_id: bool = False,  # whether to enable tracing for the log file
)
```

This will configure the logging system to use the following options:

*   Logging directory: `"logs"`
*   Log name: `"myapp_myapp_12345.log"`
*   Logging level: `"DEBUG"`
*   Log rotation: `"1 GB"`
*   Log retention: `"60 days"`
*   Log backtrace: `True`
*   Log format: `"{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message} | app_name=myapp | service_id=12345"`
*   Log serializer: `True`
*   Log diagnose: `True`
*   Application name: `"myapp"`
*   Append application name: `True`
*   Service ID: `"12345"`
*   Append service ID: `True`

===================================================
### Intercepting standard logging:

The `dsg_lib.logging_config` library code also includes an interceptor for standard python logging. This allows you to capture all log messages sent through the standard python logging module and redirect them to the loguru logger.

To use the interceptor, you don't need to do anything special. It is automatically added when you call the `config_log()` function.

===================================================
### Conclusion:

In summary, the `dsg_lib.logging_config` library code provides an easy-to-use configuration and interceptor for standard python logging using the `loguru` package. The library allows you to customize the logging options to fit your needs and capture all log messages sent through the standard python logging module.