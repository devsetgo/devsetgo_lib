# =============================================================================
# Project Variables
# =============================================================================
REPONAME = devsetgo_lib
APP_VERSION = 2026-03-15-001

# Python Configuration
PYTHON = python3
PIP = $(PYTHON) -m pip
PYTEST = $(PYTHON) -m pytest

# Path Configuration
EXAMPLE_PATH = examples
SERVICE_PATH = dsg_lib
TESTS_PATH = tests
SQLITE_PATH = _sqlite_db
LOG_PATH = log

# Server Configuration
PORT = 5000
WORKER = 8
LOG_LEVEL = debug

# Requirements
REQUIREMENTS_PATH = requirements.txt
# DEV_REQUIREMENTS_PATH = requirements/dev.txt

# =============================================================================
# Safety Checks
# =============================================================================
# Make will use bash instead of sh
SHELL := /bin/bash

# Ensure user-local bin is in PATH (e.g. for pip --user installs)
export PATH := $(HOME)/.local/bin:$(PATH)

# Make will exit on errors
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c

# Delete target files if the command fails
.DELETE_ON_ERROR:

# Warn if variables are undefined
MAKEFLAGS += --warn-undefined-variables

# Disable built-in implicit rules
.SUFFIXES:

# =============================================================================
# Phony Targets
# =============================================================================
.PHONY: help all autoflake black build bump check-deps clean cleanup create-docs create-docs-dev \
        create-docs-local delete-version dev-setup format install isort list-docs \
        migrate-legacy-docs pre-commit quick-test rebase reinstall ruff serve-docs \
        set-default-version sync-docs-branch test test-coverage tests validate \
        ex-fastapi ex-log ex-cal ex-csv ex-json ex-pattern ex-text ex-email ex-fm ex-fm-timer ex-all \
        speedtest flake8

# =============================================================================
# Default Target
# =============================================================================
.DEFAULT_GOAL := help

# =============================================================================
# Help Target
# =============================================================================
help:  ## Display this help message
	@echo ""
	@printf "\033[0;36m████████████████████████████████████████████████████████████████\033[0m\n"
	@printf "\033[0;36m█                    \033[1;37m$(REPONAME) Makefile\033[0;36m                     █\033[0m\n"
	@printf "\033[0;36m████████████████████████████████████████████████████████████████\033[0m\n"
	@awk 'BEGIN {FS = ":.*##"; printf "\n\033[1;37mUsage:\033[0m\n  make \033[0;36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[0;36m%-20s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1;33m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)
	@echo ""

##@ Quick Start
all: install format test build ## Run the complete development workflow
	@printf "\033[0;32m✅ Complete workflow finished successfully!\033[0m\n"

dev-setup: install pre-commit ## Set up development environment
	@printf "\033[0;32m✅ Development environment set up successfully!\033[0m\n"

quick-test: format ## Run quick tests (no pre-commit hooks)
	@printf "\033[1;33m🧪 Running quick tests...\033[0m\n"
	$(PYTEST)
	@printf "\033[0;32m✅ Quick tests passed!\033[0m\n"

##@ Build and Version Management
build: ## Build the project
	@printf "\033[1;33m📦 Building project...\033[0m\n"
	$(PYTHON) -m build
	@printf "\033[0;32m✅ Build completed successfully!\033[0m\n"

bump: ## Bump calver version
	@printf "\033[1;33m📈 Bumping version...\033[0m\n"
	bumpcalver --build
	@printf "\033[0;32m✅ Version bumped successfully!\033[0m\n"

##@ Code Formatting and Linting
autoflake: ## Remove unused imports and unused variables from Python code
	@printf "\033[1;33m🧹 Removing unused imports and variables...\033[0m\n"
	autoflake --in-place --remove-all-unused-imports --ignore-init-module-imports --remove-unused-variables -r $(SERVICE_PATH)
	autoflake --in-place --remove-all-unused-imports --ignore-init-module-imports --remove-unused-variables -r $(TESTS_PATH)
	autoflake --in-place --remove-all-unused-imports --ignore-init-module-imports --remove-unused-variables -r $(EXAMPLE_PATH)
	@printf "\033[0;32m✅ Autoflake completed!\033[0m\n"

black: ## Reformat Python code to follow the Black code style
	@printf "\033[1;33m🖤 Formatting code with Black...\033[0m\n"
	black $(SERVICE_PATH) $(TESTS_PATH) $(EXAMPLE_PATH)
	@printf "\033[0;32m✅ Black formatting completed!\033[0m\n"

cleanup: format ## Run all code formatting tools (alias for format)
	@printf "\033[0;32m✅ Code cleanup completed!\033[0m\n"

format: isort ruff autoflake black ## Run all code formatting tools in the correct order
	@printf "\033[0;32m✅ All formatting tools completed!\033[0m\n"

isort: ## Sort imports in Python code
	@printf "\033[1;33m📚 Sorting imports with isort...\033[0m\n"
	isort $(SERVICE_PATH) $(TESTS_PATH) $(EXAMPLE_PATH)
	@printf "\033[0;32m✅ Import sorting completed!\033[0m\n"

ruff: ## Format Python code with Ruff
	@printf "\033[1;33m🦀 Linting and fixing with Ruff...\033[0m\n"
	ruff check --fix --exit-non-zero-on-fix --show-fixes $(SERVICE_PATH) || true
	ruff check --fix --exit-non-zero-on-fix --show-fixes $(TESTS_PATH) || true
	ruff check --fix --exit-non-zero-on-fix --show-fixes $(EXAMPLE_PATH) || true
	@printf "\033[0;32m✅ Ruff linting completed!\033[0m\n"

validate: ## Validate code without making changes
	@printf "\033[1;33m🔍 Validating code style...\033[0m\n"
	black --check $(SERVICE_PATH) $(TESTS_PATH) $(EXAMPLE_PATH)
	isort --check-only $(SERVICE_PATH) $(TESTS_PATH) $(EXAMPLE_PATH)
	ruff check $(SERVICE_PATH) $(TESTS_PATH) $(EXAMPLE_PATH)
	@printf "\033[0;32m✅ Code validation passed!\033[0m\n"

flake8: ## Run flake8 to check Python code for PEP8 compliance
	@printf "\033[1;33m📋 Running flake8 checks...\033[0m\n"
	flake8 --tee . > htmlcov/_flake8Report.txt
	@printf "\033[0;32m✅ Flake8 completed!\033[0m\n"

##@ Documentation Management
create-docs: sync-docs-branch ## Build and deploy the project's documentation with versioning
	@printf "\033[1;33m📚 Building and deploying documentation...\033[0m\n"
	python3 scripts/changelog.py
	python3 scripts/update_docs.py
	cp /workspaces/$(REPONAME)/README.md /workspaces/$(REPONAME)/docs/index.md
	cp /workspaces/$(REPONAME)/CONTRIBUTING.md /workspaces/$(REPONAME)/docs/contribute.md
	cp /workspaces/$(REPONAME)/CHANGELOG.md /workspaces/$(REPONAME)/docs/release-notes.md
	python3 scripts/deploy_docs.py deploy --push --ignore-remote-status
	@printf "\033[0;32m✅ Documentation deployed successfully!\033[0m\n"

create-docs-dev: sync-docs-branch ## Build and deploy a development version of the documentation
	@printf "\033[1;33m📚 Building and deploying dev documentation...\033[0m\n"
	python3 scripts/changelog.py
	python3 scripts/update_docs.py
	cp /workspaces/$(REPONAME)/README.md /workspaces/$(REPONAME)/docs/index.md
	cp /workspaces/$(REPONAME)/CONTRIBUTING.md /workspaces/$(REPONAME)/docs/contribute.md
	cp /workspaces/$(REPONAME)/CHANGELOG.md /workspaces/$(REPONAME)/docs/release-notes.md
	python3 scripts/deploy_docs.py deploy --dev --version dev --push --ignore-remote-status
	@printf "\033[0;32m✅ Dev documentation deployed successfully!\033[0m\n"

create-docs-local: ## Build and deploy the project's documentation locally with versioning
	@printf "\033[1;33m📚 Building documentation locally...\033[0m\n"
	python3 scripts/changelog.py
	python3 scripts/update_docs.py
	cp /workspaces/$(REPONAME)/README.md /workspaces/$(REPONAME)/docs/index.md
	cp /workspaces/$(REPONAME)/CONTRIBUTING.md /workspaces/$(REPONAME)/docs/contribute.md
	cp /workspaces/$(REPONAME)/CHANGELOG.md /workspaces/$(REPONAME)/docs/release-notes.md
	python3 scripts/deploy_docs.py deploy
	@printf "\033[0;32m✅ Local documentation built successfully!\033[0m\n"

delete-version: ## Delete a specific documentation version (requires VERSION parameter)
	@printf "\033[1;33m🗑️ Deleting documentation version $(VERSION)...\033[0m\n"
	python3 scripts/deploy_docs.py delete --version $(VERSION) --push
	@printf "\033[0;32m✅ Version $(VERSION) deleted successfully!\033[0m\n"

list-docs: ## List all deployed documentation versions
	@printf "\033[1;33m📋 Listing documentation versions...\033[0m\n"
	python3 scripts/deploy_docs.py list

migrate-legacy-docs: ## Migrate legacy documentation to versioned structure (run once)
	@printf "\033[1;33m🚀 Migrating legacy documentation to Mike versioning...\033[0m\n"
	python3 scripts/migrate_legacy_docs.py
	@printf "\033[0;32m✅ Legacy documentation migrated!\033[0m\n"

serve-docs: ## Serve all documentation versions locally
	@printf "\033[1;33m🌐 Serving documentation locally...\033[0m\n"
	python3 scripts/deploy_docs.py serve

set-default-version: ## Set the default version for documentation (requires VERSION parameter)
	@printf "\033[1;33m🔧 Setting default version to $(VERSION)...\033[0m\n"
	mike set-default $(VERSION)
	@printf "\033[0;32m✅ Default version set successfully!\033[0m\n"

sync-docs-branch: ## Sync local gh-pages with remote before deployment
	@printf "\033[1;33m🔄 Syncing gh-pages branch...\033[0m\n"
	git fetch origin gh-pages 2>/dev/null || echo "Remote gh-pages branch not found"
	git stash push -m "Temporary stash for docs sync" || echo "No changes to stash"
	if git show-ref --verify --quiet refs/heads/gh-pages; then \
		echo "Local gh-pages branch exists, switching to it"; \
		git checkout gh-pages; \
	else \
		echo "Creating new gh-pages branch"; \
		git checkout -b gh-pages; \
	fi
	git reset --hard origin/gh-pages 2>/dev/null || echo "New gh-pages branch"
	git checkout dev
	git stash pop || echo "No stash to restore"
	@printf "\033[0;32m✅ Branch sync completed!\033[0m\n"

##@ Git Operations
rebase: ## Rebase the current branch onto the main branch
	@printf "\033[1;33m🔄 Rebasing onto main...\033[0m\n"
	git fetch origin main
	git rebase origin/main
	@printf "\033[0;32m✅ Rebase completed!\033[0m\n"

##@ Maintenance and Cleanup
check-deps: ## Check for outdated dependencies
	@printf "\033[1;33m🔍 Checking for outdated dependencies...\033[0m\n"
	$(PIP) list --outdated
	@printf "\033[0;32m✅ Dependency check completed!\033[0m\n"

clean: ## Clean up generated files and caches
	@printf "\033[1;33m🧹 Cleaning up...\033[0m\n"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type f -name "*.pyd" -delete 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ .pytest_cache/ .ruff_cache/ 2>/dev/null || true
	@printf "\033[0;32m✅ Cleanup completed!\033[0m\n"

##@ Setup and Installation
install: ## Install the project's dependencies
	@printf "\033[1;33m📦 Installing dependencies...\033[0m\n"
	$(PIP) install -r $(REQUIREMENTS_PATH)
	@printf "\033[0;32m✅ Dependencies installed successfully!\033[0m\n"

pre-commit: ## Set up pre-commit hooks
	@printf "\033[1;33m🔗 Setting up pre-commit hooks...\033[0m\n"
	pre-commit install
	@printf "\033[0;32m✅ Pre-commit hooks installed!\033[0m\n"

reinstall: clean ## Clean and reinstall the project's dependencies
	@printf "\033[1;33m♻️  Reinstalling dependencies...\033[0m\n"
	$(PIP) uninstall -r $(REQUIREMENTS_PATH) -y
	$(PIP) install -r $(REQUIREMENTS_PATH)
	@printf "\033[0;32m✅ Dependencies reinstalled successfully!\033[0m\n"

##@ Testing and Quality Assurance
test: ## Run the project's tests with pre-commit hooks
	@printf "\033[1;33m🧪 Running full test suite...\033[0m\n"
	pre-commit run -a
	$(PYTEST) --cov=$(SERVICE_PATH) --cov-report=xml --cov-report=html --junitxml=report.xml
	sed -i 's|<source>.*</source>|<source>$(SERVICE_PATH)</source>|' coverage.xml
	genbadge coverage -i coverage.xml
	genbadge tests -i report.xml
	@printf "\033[0;32m✅ All tests passed!\033[0m\n"

test-coverage: ## Run tests and generate coverage report
	@printf "\033[1;33m📊 Generating coverage report...\033[0m\n"
	$(PYTEST) --cov=$(SERVICE_PATH) --cov-report=html --cov-report=term-missing
	@printf "\033[0;32m✅ Coverage report generated in htmlcov/\033[0m\n"

tests: test ## Alias for test target

##@ Performance Testing
speedtest: ## Run a speed test
	@printf "\033[1;33m🏁 Running speed test...\033[0m\n"
	if [ ! -f speedtest/http_request.so ]; then gcc -shared -o speedtest/http_request.so speedtest/http_request.c -lcurl -fPIC; fi
	python3 speedtest/loop.py
	@printf "\033[0;32m✅ Speed test completed!\033[0m\n"

##@ Example Applications
ex-fastapi: ## Run the example FastAPI application
	@printf "\033[1;33m🚀 Starting FastAPI example...\033[0m\n"
	uvicorn examples.fastapi_example:app --port ${PORT} --reload --log-level $(LOG_LEVEL)

ex-log: ## Run the example logging script
	@printf "\033[1;33m📝 Running logging example...\033[0m\n"
	python3 examples/log_example.py
	@printf "\033[0;32m✅ Logging example completed!\033[0m\n"

ex-cal: ## Run the example calendar script
	@printf "\033[1;33m📅 Running calendar example...\033[0m\n"
	python3 examples/cal_example.py
	@printf "\033[0;32m✅ Calendar example completed!\033[0m\n"

ex-csv: ## Run the example CSV script
	@printf "\033[1;33m📊 Running CSV example...\033[0m\n"
	python3 examples/csv_example.py
	@printf "\033[0;32m✅ CSV example completed!\033[0m\n"

ex-json: ## Run the example JSON script
	@printf "\033[1;33m🔗 Running JSON example...\033[0m\n"
	python3 examples/json_example.py
	@printf "\033[0;32m✅ JSON example completed!\033[0m\n"

ex-pattern: ## Run the example pattern script
	@printf "\033[1;33m🔍 Running pattern example...\033[0m\n"
	python3 examples/pattern_example.py
	@printf "\033[0;32m✅ Pattern example completed!\033[0m\n"

ex-text: ## Run the example text script
	@printf "\033[1;33m📄 Running text example...\033[0m\n"
	python3 examples/text_example.py
	@printf "\033[0;32m✅ Text example completed!\033[0m\n"

ex-email: ## Run the example email validation script
	@printf "\033[1;33m📧 Running email validation example...\033[0m\n"
	python3 examples/validate_emails.py
	@printf "\033[0;32m✅ Email validation example completed!\033[0m\n"

ex-fm: ## Run the example file monitor script
	@printf "\033[1;33m👁️ Running file monitor example...\033[0m\n"
	python3 examples/file_monitor.py
	@printf "\033[0;32m✅ File monitor example completed!\033[0m\n"

ex-fm-timer: ## Run the CSV example with timer
	@printf "\033[1;33m⏱️ Running CSV with timer example...\033[0m\n"
	python3 examples/csv_example_with_timer.py
	@printf "\033[0;32m✅ CSV with timer example completed!\033[0m\n"

ex-all: ex-log ex-cal ex-csv ex-json ex-pattern ex-text ex-email ex-fm ex-fm-timer ## Run all the examples except FastAPI
	@printf "\033[0;32m✅ All examples completed!\033[0m\n"
