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

A set of common functions wrapped into a package, so I don't have to write the same code over and over. Oh and it makes the code more reusable.... or something like that.

### Testing
Test on Windows and Linux. Since I work in Windows and Linux I test for issues there. Should work on MacOS, but let me know if there is an issue.

### Library Functions

- Common Functions
    - file_functions
        - CSV File Functions
        - JSON File Functions
        - Text File Functions

    - Folder Functions
        - Make Directory
        - Remove Directory
        - Last File Changed
        - Directory List

    - Calendar Functions
        - Get Month
        - Get Month Number

    - Patterns
        - Pattern Between Two Characters

    - Logging
        - logging configuration and interceptor

- FastAPI Endpoints
    - Systems Health Endpoints
        - Status/Health, Heapdump, Uptime
    - HTTP Codes
        - Way to generate HTTP response codes

- Aysnc Database
    - Database Config
    - Async Session
    - Database Operations (CRUD)
