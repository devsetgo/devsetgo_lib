Python:

[![PyPI version fury.io](https://badge.fury.io/py/devsetgo-lib.svg)](https://pypi.python.org/pypi/devsetgo-lib/)
[![Downloads](https://static.pepy.tech/badge/devsetgo-lib)](https://pepy.tech/project/devsetgo-lib)
[![Downloads](https://static.pepy.tech/badge/devsetgo-lib/month)](https://pepy.tech/project/devsetgo-lib)
[![Downloads](https://static.pepy.tech/badge/devsetgo-lib/week)](https://pepy.tech/project/devsetgo-lib)

Support Python Versions

![Static Badge](https://img.shields.io/badge/Python-3.12%20%7C%203.11%20%7C%203.10%20%7C%203.9-blue)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)


CI/CD Pipeline:

[![Testing - Main](https://github.com/devsetgo/devsetgo_lib/actions/workflows/testing.yml/badge.svg?branch=main)](https://github.com/devsetgo/devsetgo_lib/actions/workflows/testing.yml)
[![Testing - Dev](https://github.com/devsetgo/devsetgo_lib/actions/workflows/testing.yml/badge.svg?branch=dev)](https://github.com/devsetgo/devsetgo_lib/actions/workflows/testing.yml)
[![Coverage fury.io](coverage-badge.svg)](https://github.com/devsetgo/dsg_lib)

SonarCloud:

[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=devsetgo_devsetgo_lib&metric=coverage)](https://sonarcloud.io/dashboard?id=devsetgo_devsetgo_lib)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=devsetgo_devsetgo_lib&metric=sqale_rating)](https://sonarcloud.io/dashboard?id=devsetgo_devsetgo_lib)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=devsetgo_devsetgo_lib&metric=alert_status)](https://sonarcloud.io/dashboard?id=devsetgo_devsetgo_lib)

[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=devsetgo_devsetgo_lib&metric=reliability_rating)](https://sonarcloud.io/dashboard?id=devsetgo_devsetgo_lib)
[![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=devsetgo_devsetgo_lib&metric=vulnerabilities)](https://sonarcloud.io/dashboard?id=devsetgo_devsetgo_lib)

![Static Badge](https://img.shields.io/badge/Documentation-v0.12.2-blue?link=https%3A%2F%2Fdevsetgo.github.io%2Fdevsetgo_lib)


# DevSetGo Common Library

## Introduction
The DevSetGo Common Library is a comprehensive package of common functions designed to eliminate repetitive coding and enhance code reusability. It aims to save developers time and effort across various projects.

## Compatibility and Testing
- **Tested on**: Windows, Linux.
- **Compatibility**: Potentially compatible with MacOS (feedback on issues is appreciated).

## Library Functions
### Common Functions
- **File Functions**:
  - CSV File Functions
  - JSON File Functions
  - Text File Functions
- **Folder Functions**:
  - Make Directory
  - Remove Directory
  - Last File Changed
  - Directory List
- **Calendar Functions**:
  - Get Month
  - Get Month Number
- **Patterns**:
  - Pattern Between Two Characters
- **Logging**:
  - Logging configuration and interceptor

### FastAPI Endpoints
- **Systems Health Endpoints**:
  - Status/Health, Heapdump, Uptime
- **HTTP Codes**:
  - Method to generate HTTP response codes

### Async Database
- Database Config
- Async Session
- CRUD Operations

## Examples and Usage
Refer to the [Recipes Pages](https://devsetgo.github.io/devsetgo_lib/recipes/fastapi/)

## Installation Guide
[Quick Start](https://devsetgo.github.io/devsetgo_lib/quickstart/)

```python
pip install devsetgo-lib

# Aysync database setup
pip install devsetgo-lib[sqlite]
pip install devsetgo-lib[postgres]

# Consider these experimental and untested
pip install devsetgo-lib[oracle]
pip install devsetgo-lib[mssql]
pip install devsetgo-lib[mysql]

# For adding FastAPI endpoints
pip install devsetgo-lib[fastapi]

# Install everything
pip install devsetgo-lib[all]
```


## Contribution and Feedback
Contributions and feedback are highly appreciated. Please refer to our [Contribution Guidelines](https://github.com/devsetgo/devsetgo_lib/blob/main/CONTRIBUTING.md).

## License
[MIT Licensed](https://github.com/devsetgo/devsetgo_lib/blob/main/LICENSE)

## Author Information
[Mike Ryan](https://github.com/devsetgo)

## Further Documentation
For more detailed information, visit [LINK_TO_DETAILED_DOCUMENTATION](https://devsetgo.github.io/devsetgo_lib/).
