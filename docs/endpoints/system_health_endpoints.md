# dsg_lib.fastapi.system_health_endpoints

This module is part of the `dsg_lib.fastapi` package. It provides a configurable health endpoint for your FastAPI application. It includes the following routes:

- `/api/health/status`: Returns the status of the application. If the application is running, it will return `{"status": "UP"}`. This endpoint can be enabled or disabled using the configuration.

- `/api/health/uptime`: Returns the uptime of the application in a dictionary with the keys "Days", "Hours", "Minutes", and "Seconds". The uptime is calculated from the time the application was started. This endpoint can be enabled or disabled using the configuration.

- `/api/health/heapdump`: Returns a heap dump of the application. The heap dump is a list of dictionaries, each representing a line of code. Each dictionary includes the filename, line number, size of memory consumed, and the number of times the line is referenced. This endpoint can be enabled or disabled using the configuration.

## Installation

This module is part of the `dsg_lib` package. To install the package, use pip:

```bash
pip install dsg_lib
```

## Usage

To use the function in this module, you need to import it from the `dsg_lib.fastapi.system_health_endpoints` package. Here's how you can do it:

```python
from dsg_lib.fastapi.system_health_endpoints import create_health_router
```

Then, you can create a health router with the desired configuration and include it in your FastAPI application:

```python
from FastAPI import FastAPI
from dsg_lib.fastapi.system_health_endpoints import create_health_router

app = FastAPI()

# User configuration
config = {
    "enable_status_endpoint": True,
    "enable_uptime_endpoint": False,
    "enable_heapdump_endpoint": True,
}

# Health router
health_router = create_health_router(config)
app.include_router(health_router, prefix="/api/health", tags=["system-health"])
```

## Purpose

The purpose of this module is to provide a simple and efficient way to monitor the health of your FastAPI application. It allows you to check the status, uptime, and memory usage of your application, which can be useful for debugging and performance tuning.