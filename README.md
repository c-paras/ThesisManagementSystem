# ThesisManagementSystem
A system for organizing, allocating, submitting and marking final-year university theses

## Description
This system is designed to offer a central platform for managing each step of the university thesis process. Thesis administrators can create courses, provide relevant material and add tasks to be completed. Students are able to find and request topics offered by supervisors, submit their work and receive their feedback. Thesis supervisors can create and offer topics, mark submitted work and assign assessors.

## Getting Started

### Prerequisites
It is assumed that:
* [Python 3.6.8](https://www.python.org/downloads/) or above is installed
* [SQLite 3.22.0](https://www.sqlite.org/download.html) or above is installed
* [JSHint 2.10.2](https://jshint.com/install/) or above is installed

### Installation

Run the following commands to initialize the project:

```sh
# Install Python requirements
pip3 install -r requirements.txt

# Set up linters in a UNIX environment
sh config.sh

# Initialize an empty database
sqlite3 db/thesis.db < db/schema.sql
```

## Usage

Run the Python Flask server with the following command:
```sh
python3 server.py
```
Then navigate to <http://localhost:5000>.
The server should restart automatically upon changing the project files.

## Project Structure
* `app/` - Python server blueprints
* `db/` - database-related files
* `static/` - CSS and JS files
* `templates/` - Jinja2 HTML templates

## Contributing
1. Clone the repository (`git clone git@github.com:costaparas/ThesisManagementSystem.git`)
2. Create a new feature branch (`git checkout -b foobar-feature`)
3. Commit new changes (`git commit -a -m 'add foobar'`)
4. Push to the branch (`git push origin foobar-feature`)
5. Create a new [Pull Request](https://github.com/costaparas/ThesisManagementSystem/pulls>)
6. Merge the Pull Request once it is approved by at least one other contributor

## License
Copyright (C) 2019 Dominic McDonald, Costa Paraskevopoulos, Troy Murray, Alexander Hodges, Chang Ge, Rohan Bhat

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <http://www.gnu.org/licenses/>.
