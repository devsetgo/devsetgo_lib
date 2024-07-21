# Variables
PYTHON = python3
PIP = $(PYTHON) -m pip
PYTEST = $(PYTHON) -m pytest

EXAMPLE_PATH = examples
SERVICE_PATH = dsg_lib
TESTS_PATH = tests
SQLITE_PATH = _sqlite_db
LOG_PATH = log

PORT = 5000
WORKER = 8
LOG_LEVEL = debug

REQUIREMENTS_PATH = requirements.txt
# DEV_REQUIREMENTS_PATH = requirements/dev.txt

.PHONY: autoflake black cleanup create-docs flake8 help install isort run-example run-example-dev speedtest test

autoflake: ## Remove unused imports and unused variables from Python code
	autoflake --in-place --remove-all-unused-imports  --ignore-init-module-imports --remove-unused-variables -r $(SERVICE_PATH)
	autoflake --in-place --remove-all-unused-imports  --ignore-init-module-imports --remove-unused-variables -r $(TESTS_PATH)
	autoflake --in-place --remove-all-unused-imports  --ignore-init-module-imports --remove-unused-variables -r $(EXAMPLE_PATH)

black: ## Reformat Python code to follow the Black code style
	black $(SERVICE_PATH)
	black $(TESTS_PATH)
	black $(EXAMPLE_PATH)

bump-minor: ## Bump the minor version number x.1.0
	bump2version minor

bump-release: ## Bump the release version number x.x.x-beta.1
	bump2version release

bump-patch: ## Bump the patch version number x.x.1
	bump2version patch

cleanup: ruff autoflake flake8 ## Run ruff, autoflake, and flake8 to clean up and format Python code

create-docs: ## Build and deploy the project's documentation
	python3 scripts/changelog.py
	mkdocs build
	cp /workspaces/devsetgo_lib/README.md /workspaces/devsetgo_lib/docs/index.md
	cp /workspaces/devsetgo_lib/CONTRIBUTING.md /workspaces/devsetgo_lib/docs/contribute.md
	mkdocs gh-deploy

create-docs-local: ## Build and deploy the project's documentation
	python3 scripts/changelog.py
	mkdocs build
	cp /workspaces/devsetgo_lib/README.md /workspaces/devsetgo_lib/docs/index.md
	cp /workspaces/devsetgo_lib/CONTRIBUTING.md /workspaces/devsetgo_lib/docs/contribute.md

changelog: ## Create a changelog
	python3 scripts/changelog.py
	cp /workspaces/devsetgo_lib/CHANGELOG.md /workspaces/devsetgo_lib/docs/release-notes.md

release-docs: changelog create-docs ## Build and deploy the project's documentation

flake8: ## Run flake8 to check Python code for PEP8 compliance
	flake8 --tee . > htmlcov/_flake8Report.txt

help:  ## Display this help message
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

install: ## Install the project's dependencie
	$(PIP) install -r $(REQUIREMENTS_PATH)

reinstall: ## Install the project's dependencie
	$(PIP) uninstall -r $(REQUIREMENTS_PATH) -y
	$(PIP) install -r $(REQUIREMENTS_PATH)

isort: ## Sort imports in Python code
	isort $(SERVICE_PATH)
	isort $(TESTS_PATH)
	isort $(EXAMPLE_PATH)

run-fastapi: ## Run the example application
	uvicorn examples.fastapi_example:app --port ${PORT} --reload  --log-level $(LOG_LEVEL)
	# uvicorn examples.fastapi_example:app --port ${PORT} --workers ${WORKER}  --log-level $(LOG_LEVEL)

speedtest: ## Run a speed test
	if [ ! -f speedtest/http_request.so ]; then gcc -shared -o speedtest/http_request.so speedtest/http_request.c -lcurl -fPIC; fi
	python3 speedtest/loop.py

test: ## Run the project's tests
	pre-commit run -a
	pytest
	sed -i 's|<source>/workspaces/devsetgo_lib</source>|<source>/github/workspace</source>|' /workspaces/devsetgo_lib/coverage.xml
	genbadge coverage -i /workspaces/dsg/coverage.xml
	flake8 --tee . > htmlcov/_flake8Report.txt
#flake8 --max-doc-length=132 --tee . > htmlcov/_flake8Report.txt

build: ## Build the project
	python -m build

ruff: ## Format Python code with Ruff
	ruff check --fix --exit-non-zero-on-fix --show-fixes $(SERVICE_PATH)
	ruff check --fix --exit-non-zero-on-fix --show-fixes $(TESTS_PATH)
	ruff check --fix --exit-non-zero-on-fix --show-fixes $(EXAMPLE_PATH)
