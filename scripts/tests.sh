#!/bin/bash
set -e
set -x

# run isort recursively
# isort -rc .

#run pre-commit
pre-commit run -a

# bash scripts/test.sh --cov-report=html ${@}
python3 -m pytest
# python3 -m pytest -v -s
# modify path for
sed -i "s/<source>\/home\/mike\/devsetgo_lib<\/source>/<source>\/github\/workspace<\/source>/g" ~/devsetgo_lib/coverage.xml
# create coverage-badge
coverage-badge -o ../coverage.svg -f

# generate flake8 report
# flake8 --tee . > flake8_report/report.txt
