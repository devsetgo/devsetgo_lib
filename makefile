# Define the virtual environment directory
VENV_DIR = _venv

# Define the source directory
SRC_DIR = dsg_lib

# Define the test directory
TEST_DIR = tests

# Define the requirements file
REQ_FILE = requirements.txt
REQ_FILE_DEV = requirements-dev.txt

# Define the scripts directory
SCRIPTS_DIR = scripts

# Define the flake8 report directory
FLAKE8_REPORT_DIR = flake8_report

# Define common commands
PIP = pip3
PYTHON = python3

.PHONY: all autoflake clean flake8 format install install-dev test upgrade venv

# Default target
all: autoflake clean format install install-dev test upgrade venv flake8

# Remove unused imports and variables using autoflake
autoflake:
	./$(SCRIPTS_DIR)/autoflake.sh

# Remove virtual environment
clean:
	rm -rf $(VENV_DIR)

# Run flake8 to check for code style errors
#mkdir -p $(FLAKE8_REPORT_DIR)
#flake8 --tee . > $(FLAKE8_REPORT_DIR)/report.txt
flake8:
	./scripts/flake8.sh

# Format code using isort and black
format:
	isort $(SRC_DIR) $(TEST_DIR)
	black $(SRC_DIR) $(TEST_DIR)

# Install requirements from source directory
install:
	$(PIP) install --upgrade pip setuptools
	$(PIP) install -r $(REQ_FILE) --use-deprecated=legacy-resolver

# Install development requirements from source directory
install-dev:
	$(PIP) install --upgrade pip setuptools
	$(PIP) install -r $(REQ_FILE_DEV) --use-deprecated=legacy-resolver

# Run tests via pre-commit and pytest
test:
	pre-commit run -a
	pytest
	sed -i 's|<source>/workspaces/devsetgo_lib</source>|<source>/github/workspace</source>|' /workspaces/devsetgo_lib/coverage.xml
	coverage-badge -o coverage.svg -f

# Upgrade pip to the latest version
upgrade:
	$(PIP) install --upgrade pip

# Create the virtual environment
venv:
	$(PYTHON) -m venv $(VENV_DIR)

# Upgrade pip and recreate the virtual environment
venv-update: upgrade venv

# Create a requirements file for the virtual environment
venv-requirements:
	$(PIP) freeze > requirements.txt

# Install requirements for the virtual environment
venv-install:
	$(PIP) install --upgrade pip setuptools
	$(PIP) install -r requirements.txt --use-deprecated=legacy-resolver

# Run flake8 to check for code style errors in the virtual environment
venv-flake8:
	mkdir -p $(FLAKE8_REPORT_DIR)
	$(VENV_DIR)/bin/flake8 --tee . > $(FLAKE8_REPORT_DIR)/report.txt

# Remove the virtual environment
venv-clean:
	rm -rf $(VENV_DIR)
