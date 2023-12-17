# -*- coding: utf-8 -*-
"""Setup script for realpython-reader"""

import os.path

from setuptools import setup, find_packages

# The directory containing this file
HERE = os.path.abspath(os.path.dirname(__file__))

# The text of the README file
with open(os.path.join(HERE, "README.md")) as fid:
    README = fid.read()

# This call to setup() does all the work
setup(
    name="devsetgo_lib",
    version="0.11.0-beta3",
    description="DevSetGo Common Library provides reusable Python functions for enhanced code efficiency. It includes utilities for file operations, calendar, pattern matching, logging, FastAPI endpoints, and async database handling with CRUD operations.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/devsetgo/dev_com_lib",
    project_urls={
        "Documentation": "https://devsetgo.github.io/devsetgo_lib/",
        "Source": "https://github.com/devsetgo/devsetgo_lib",
    },
    keywords=[
        "Python",
        "Asyncio",
        "Reusable Functions",
        "File Operations",
        "Folder Management",
        "Calendar Utilities",
        "Pattern Matching",
        "Logging",
        "FastAPI",
        "HTTP Codes",
        "Asynchronous Database",
        "CRUD Operations",
        "Code Efficiency",
        "Maintainability",
    ],
    author="Mike Ryan",
    author_email="mikeryan56@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: POSIX :: Linux",
        "Operating System :: POSIX",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
    python_requires=">=3.9",
    # packages=find_packages(where="dsg_lib"),
    packages=["dsg_lib"],
    include_package_data=True,
    install_requires=[
        "loguru>=0.7.0",
        "packaging>=20.0",
    ],
    extras_require={
        "postgres": ["asyncpg>=0.21.0", "sqlalchemy>=2.0.10,<2.0.99"],
        "sqlite": ["aiosqlite>=0.17.0", "sqlalchemy>=2.0.10,<2.0.99"],
        "oracle": ["cx_Oracle>=8.0.0", "sqlalchemy>=2.0.10,<2.0.99"],
        "mssql": ["aioodbc>=0.4.1", "sqlalchemy>=2.0.10,<2.0.99"],
        "fastapi": ["fastapi>=0.100.0", "pydantic[email]>=2.0"],
        "all": [
            "asyncpg>=0.21.0",
            "sqlalchemy>=2.0.10,<2.0.99",
            "aiosqlite>=0.17.0",
            "cx_Oracle>=8.0.0",
            "fastapi>=0.100.0",
            "pydantic[email]>=2.0",
            "aioodbc>=0.4.1",
        ],
    },
)
