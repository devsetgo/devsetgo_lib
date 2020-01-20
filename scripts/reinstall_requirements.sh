#!/bin/bash
set -e
set -x

# remove current libraries
pip3 uninstall -r requirements/dev.txt -y

# install requirements
pip3 install -r requirements/dev.txt