#!/bin/bash
set -e
set -x

# mkdocs
mkdocs build

# Copy Contribute to Github Contributing
cp ~/devsetgo_lib/docs/contribute.md ~/devsetgo_lib/CONTRIBUTING.md