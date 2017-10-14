# itucsdb1739
ITUPass - BLG361E Database Lecture Project

[![Documentation Status](https://readthedocs.org/projects/itucsdb1739/badge/?version=latest)](http://itucsdb1739.readthedocs.io/en/latest/?badge=latest)

# Project resources
* [Source Code](https://github.com/itucsdb1739/itucsdb1739)
* [Weekly Reports](https://github.com/itucsdb1739/itucsdb1739/wiki)
* [Demo Page](https://itucsdb1739.mybluemix.net/)
* [Documentation](https://itucsdb1739.readthedocs.io/en/latest/)

# Quick Start:
* `pip install --editable .`
* `export FLASK_APP=itupass`
* `export FLASK_DEBUG=1` (optional)
* `export SECRET_KEY=Not#So@Secret` (optional)
* `export DATABASE_URI=postgresql://username@password@server.domain:5432/database`
* `flask initdb`
* `flask run`

# i18n:
* generate pot file: `pybabel extract -F babel.cfg -o itupass/translations/messages.pot itupass`
* Initialize po files: `pybabel init -i itupass/translations/messages.pot -d translations -l tr`
* Compile translations: `pybabel compile -d itupass/translations`
* Update translations from template: `pybabel update -i itupass/translations/messages.pot -d translations`

# Notice
This is a university project for BLG361E Database lecture and code contributions are not allowed till December 27, 2017

Feel free to submit issues.

# License
[BSD 3-Clause License](https://github.com/itucsdb1739/itucsdb1739/blob/master/LICENSE)

Copyright (c) 2017, Emin Mastizada. All rights reserved.
