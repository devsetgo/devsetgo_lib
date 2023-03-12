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

*   `logging_directory`: The folder for logging files. The default value is `"log"`.
*   `log_name`: The file name of the log. The default value is `"log.log"`.
*   `logging_level`: The logging level. The available values are `"DEBUG"`, `"INFO"`, `"ERROR"`, `"WARNING"`, and `"CRITICAL"`. The default value is `"INFO"`.
*   `log_rotation`: The maximum size of the log file before it rotates. The default value is `"10 MB"`.
*   `log_retention`: How long to keep the logs. The default value is `"30 days"`.
*   `log_backtrace`: Enable backtrace in the logs. The default value is `False`.
*   `log_format`: The format pattern for the logs. The default value is `"{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}"`.
*   `log_serializer`: Enable serialization in the logs. The default value is `False`.
*   `log_diagnose`: Enable diagnose in the logs. The default value is `False`.
*   `app_name`: The name of the application. The default value is `None`.
*   `append_app_name`: Append the application name to the log file name. The default value is `False`.
*   `service_id`: The service ID. The default value is `None`.
*   `append_service_id`: Append the service ID to the log file name. The default value is `False`.


===================================================
### Example:

```python
from dsg_lib.logging_config import config_log

config_log(
    logging_directory="logs",
    log_name="myapp.log",
    logging_level="DEBUG",
    log_rotation="1 GB",
    log_retention="60 days",
    log_backtrace=True,
    log_format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
    log_serializer=True,
    log_diagnose=True,
    app_name="myapp",
    append_app_name=True,
    service_id="12345",
    append_service_id=True,
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