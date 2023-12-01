# Variables
PYTHON = python3
PIP = $(PYTHON) -m pip
PYTEST = $(PYTHON) -m pytest

EXAMPLE_PATH = example
SERVICE_PATH = devsetgo_toolkit
TESTS_PATH = tests
SQLITE_PATH = _sqlite_db
LOG_PATH = log

PORT = 5000
WORKER = 8
LOG_LEVEL = debug

VENV_PATH = _venv
REQUIREMENTS_PATH = requirements.txt
# DEV_REQUIREMENTS_PATH = requirements/dev.txt

.PHONY: autoflake black cleanup create-docs flake8 help install isort run-example run-example-dev speedtest test

autoflake: ## Remove unused imports and unused variables from Python code
	autoflake --in-place --remove-all-unused-imports --remove-unused-variables --exclude __init__.py -r $(SERVICE_PATH)
	# autoflake --in-place --remove-all-unused-imports --remove-unused-variables --exclude __init__.py -r $(TESTS_PATH)
	# autoflake --in-place --remove-all-unused-imports --remove-unused-variables --exclude __init__.py -r $(EXAMPLE_PATH)

black: ## Reformat Python code to follow the Black code style
	black $(SERVICE_PATH)
	black $(TESTS_PATH)
	black $(EXAMPLE_PATH)

cleanup: isort black autoflake ## Run isort, black, and autoflake to clean up and format Python code

create-docs: ## Build and deploy the project's documentation
	mkdocs build
	cp /workspaces/DevSetGo_Toolkit/README.md /workspaces/DevSetGo_Toolkit/docs/index.md
	cp /workspaces/DevSetGo_Toolkit/CONTRIBUTING.md /workspaces/DevSetGo_Toolkit/docs/contribute.md
	mkdocs gh-deploy

flake8: ## Run flake8 to check Python code for PEP8 compliance
	flake8 --tee . > htmlcov/_flake8Report.txt


help:  ## Display this help message
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

install: ## Install the project's dependencie
	$(PIP) install -r $(REQUIREMENTS_PATH)

isort: ## Sort imports in Python code
	isort $(SERVICE_PATH)
	isort $(TESTS_PATH)
	isort $(EXAMPLE_PATH)

run-example: ## Run the example application
	uvicorn example.main:app --port ${PORT} --workers ${WORKER} --log-level $(LOG_LEVEL)

run-example-dev: ## Run the example application with hot reloading
	uvicorn example.main:app --port ${PORT} --reload  --log-level $(LOG_LEVEL)

speedtest: ## Run a speed test
	if [ ! -f example/http_request.so ]; then gcc -shared -o example/http_request.so example/http_request.c -lcurl -fPIC; fi
	python3 example/loop_c.py

test: ## Run the project's tests
	pre-commit run -a
	pytest
	sed -i 's|<source>/workspaces/DevSetGo_Toolkit</source>|<source>/github/workspace/DevSetGo_Toolkit</source>|' /workspaces/DevSetGo_Toolkit/coverage.xml
	coverage-badge -o coverage.svg -f
	flake8 --tee . > htmlcov/_flake8Report.txt
