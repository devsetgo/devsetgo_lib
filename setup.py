# -*- coding: utf-8 -*-
"""Setup script for realpython-reader"""

import os.path

from setuptools import setup

# The directory containing this file
HERE = os.path.abspath(os.path.dirname(__file__))

# The text of the README file
with open(os.path.join(HERE, "README.md")) as fid:
    README = fid.read()

# This call to setup() does all the work
setup(
    name="devsetgo_lib",
    version="0.10.0",
    description="Common functions for applications",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/devsetgo/dev_com_lib",
    project_urls={
        "Documentation": "https://devsetgo.github.io/devsetgo_lib/",
        "Source": "https://github.com/devsetgo/devsetgo_lib",
    },
    keywords=["file", "folder", "loguru", "logging", "CSV", "JSON", "Text", "Regex"],
    author="Mike Ryan",
    author_email="mikeryan56@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Operating System :: POSIX",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
    python_requires=">=3.8",
    packages=["dsg_lib"],
    include_package_data=True,
    install_requires=["loguru>=0.6.0"],
)
