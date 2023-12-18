Python:

[![PyPI version fury.io](https://badge.fury.io/py/devsetgo-lib.svg)](https://pypi.python.org/pypi/devsetgo-lib/)
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg">

[![Python 3.9](https://img.shields.io/badge/python-3.9-blue.svg)](https://www.python.org/downloads/release/python-390/)
[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-3100/)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)

CI/CD Pipeline:

[![Testing - Main](https://github.com/devsetgo/devsetgo_lib/actions/workflows/testing.yml/badge.svg?branch=main)](https://github.com/devsetgo/devsetgo_lib/actions/workflows/testing.yml)
[![Testing - Dev](https://github.com/devsetgo/devsetgo_lib/actions/workflows/testing.yml/badge.svg?branch=dev)](https://github.com/devsetgo/devsetgo_lib/actions/workflows/testing.yml)

SonarCloud:

[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=devsetgo_devsetgo_lib&metric=coverage)](https://sonarcloud.io/dashboard?id=devsetgo_devsetgo_lib)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=devsetgo_devsetgo_lib&metric=sqale_rating)](https://sonarcloud.io/dashboard?id=devsetgo_devsetgo_lib)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=devsetgo_devsetgo_lib&metric=alert_status)](https://sonarcloud.io/dashboard?id=devsetgo_devsetgo_lib)

[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=devsetgo_devsetgo_lib&metric=reliability_rating)](https://sonarcloud.io/dashboard?id=devsetgo_devsetgo_lib)
[![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=devsetgo_devsetgo_lib&metric=vulnerabilities)](https://sonarcloud.io/dashboard?id=devsetgo_devsetgo_lib)

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

