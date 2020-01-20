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
    name="dev_com_lib",
    version="20.01.19",
    description="Common library functions for applications",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/devsetgo/dev_com_lib",
    author="Mike Ryan",
    author_email="mikeryan56@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
    python_requires='>=3.7',
    packages=["com_lib"],
    include_package_data=True,
    # install_requires=[
    #     "feedparser", "html2text", "importlib_resources", "typing"
    # ],
    entry_points={"console_scripts": ["realpython=reader.__main__:main"]},
)
