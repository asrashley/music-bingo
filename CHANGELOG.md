# Change Log

## 0.2.1

TBD

### Added

* unit tests for client JavaScript application
* github action to build client

### Changed

* allow privacy policy to be viewed when not logged in
* default branch name to "main"

## 0.2.0

Dec 18 2022

### Added

* multi-user HTML application
* database to store songs, tracks, games, tickets and users
* database management commands to import and export from database
* CloudFormation scripts to deploy server to AWS
* support for various page sizes
* support for between 2 and 6 cards per page
* support for re-generation of a Bingo game
* Docker file to run tox tests on all supported Python versions
* new colour schemes: Christmas, Cyan, Pink and Magenta

### Changed

* new Schema for the gameTracks.json file
* removed automatic cards-per-page option
* removed artist name from the ticket wins page
* increase maximum clip duration to 120 seconds

## 0.1.0

Apr 1 2020

### Added

* audio playback of clips
* title to each Bingo game
* an INI file to store default options
* support for ffmpeg for encoding and playing MP3 files
* allowing changing number of rows and columns in a Bingo ticket
* mypy static type checking
* pylint style checking
* a pride colour scheme

### Changed

* upgrade code to use Python v3
* using multiple threads to search directories

### Breaking Changes

* Requires Python v3.6 or newer