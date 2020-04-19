# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)

## Todo

## [Unreleased]
- RegEx patterns

## [0.4.1] - Examples and Data
### Added
- Change of Github Actions to only upload Python 3.8 to CodeCov


## [0.4.0] - Examples and Data
### Added
- skipping version 0.3.0 and adding to 0.4.0
- Adding delimiter option to save_csv
    - Tests to check if delimiter > 1 character
    - set ',' if none
- Adding quotechar option to save_csv
- Tests to check if quotechar > 1 character
    - set '"' if none
- Add test of non-list to save_csv


## [0.3.0] - Examples and Data
### Added
- Adding examples (see examples folder)
- Adding file_function documentation
- Adding documents site - https://devsetgo.github.io/devsetgo_lib/


## [0.2.0] - Improvements
### Added
- Improved tests
- Improved Errors
- Improved logging


## [0.1.1] - Improved Testing Matrix
### Added
- Adding OS test matrix to include
    - Windows
    - Linux
    - MacOS
- Adding Documentation


## [0.1.0] - Initial Beta Release
### Added
- Initial Beta Release
- Folder Functions
- File Functions
- Tests
    - Github Actions on each push
    - Github Actions for publishing to Pypi (Testing)
- README basic info
- Start of documentation
- Sonar scanning
- No Flake8 issues