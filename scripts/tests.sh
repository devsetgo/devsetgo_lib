#!/bin/bash
set -e
set -x

# run isort recursively
# isort -rc .

#run pre-commit
pre-commit run -a

# bash scripts/test.sh --cov-report=html ${@}
# python3 -m pytest --disable-warnings
# with verbose on
# python3 -m pytest -v -s
# simple
python3 -m pytest

# create coverage-badge
coverage-badge -o ../coverage.svg -f

# document all libraries and their dependencies
# pip3 freeze > requirements/all_libraries_used.txt

# generate flake8 report
flake8 --tee . > flake8_report/report.txt

