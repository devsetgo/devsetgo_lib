# Makefile for Python project

# Define the virtual environment directory
VENV_DIR = _venv

# Define the source directory
SRC_DIR = dsg_lib

# Define the test directory
TEST_DIR = tests

# Default target
all: venv install test upgrade format

# Create the virtual environment
venv:
	python3 -m venv $(VENV_DIR)

# Install requirements from source directory
install:
	pip3 install --upgrade pip setuptools
	pip3 install -r requirements.txt --use-deprecated=legacy-resolver

# Run tests via pytest
test:
	./scripts/tests.sh

format:
	isort dsg_lib
	isort tests
	black dsg_lib
	black tests

# Remove virtual environment
clean:
	rm -rf $(VENV_DIR)

# This rule upgrades pip to the latest version
upgrade:
	pip install --upgrade pip
