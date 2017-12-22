Developer Guide
===============

INSTALL
-------

Project uses Flask and PostgreSQL database to work.
Add your Flask settings to `itupass/.env` file to operate, or to your server environment variables.


**Prepare Environment**::

* Create virtual environment in venv folder:
    `$ virtualenv venv -p python3`
* Install project:
    `$ pip install --editable .`
* Set flask app name:
    `$ export FLASK_APP=itupass`
    `$ export FLASK_DEBUG=1`
* Initialize database:
    `$ flask initdb`
* Run application:
    `$ flask run`

**Environment Variables**::

* `DATABASE_URI` - Database uri address (postgres://user:password@server:port/db)
* `VCAP_SERVICES` - Bluemix settings
* `SECRET_KEY` - Secret key for cookies
* `SENTRY_DSN` - Sentry (debug tool) DSN
* `TravisCI` - Check for Travis Continues Integration environment (pull request test service)

Database Design
---------------

* Main tables: `users`, `lectures`, `events`, `departments`
* `lecture_departments` used to store department information for lectures, students of which departments can take those lectures. It connects to the `lectures` table using `lecture` key and to the `departments` table using `department` key. It was used to create ManyToMany relationthip between `lectures` and `departments` tables.
* `lecture_schedule` used to store schedule information for lectures. As same lectures can have multiple schedules (like Math lectures) they are stored seperately and connected to the `lectures` table using `lecture` reference key.
* `user_lectures` is for storing lecture registrations for users (Check User Guide for more information).
* `event_categories` stores category names in multiple languages for Events.

Model Design
------------

* Models are located under `itupass/models` folder, they all has similar structure:

    .. code-block:: python

      class <Name>(object):
        @classmethod
        def get(cls, pk):
          # Get item from database using select command with identifier, can be multiple identifiers for different entities
          # Return object with same time, initialized with database result
          # If row is not found, return None, do not raise exception

        @classmethod
        def count(cls, **kwargs):
          # Use "SELECT COUNT" to get number of rows
          # Use `kwargs` to make filter, same as in `filter` function
          # Return number of rows as integer

        @classmethod
        def filter(cls, limit=10, offset=0, order="id DESC", **kwargs):
          # Use SELECT command to fetch multiple rows from database
          # Use limit and order for select command
          # offset is used for pagination
          # `kwargs` is used for filtering parameters, use `where_builder` from `Database` class to build `WHERE` clause and its dictionaty values
          # Return list of objects in same type
          # If no results, return empty array

        def delete(self):
          # Delete current object from database using identifier (Primary Key)
          # Do not return anything

        def save(self):
          # If object is new, use INSERT command to add to the database
          # If existing object (check using identifier), find differences from the one existing in database using `diffkeys`
          # Use UPDATE command to update current item in database
          # Return new object using identifier and `get` function

        class Meta:
          table_name = "database_table_name_for_object"

* `__init__` function of the object should take parameters in the same order as in schema.sql file.
* After creating model add it to itupass/models/__init__.py file for easy import.

**Create Form for each Model**:

* For safety and validations, use Forms for creating models in views.
* Forms are stored in `itupass/forms` folder.

**Creating View**:

* To show your new model in client you will need add view for it.
* Create view file under `itupass/views` folder.
* Make Blueprint variable for your view, add all views for that Blueprint.
* Add your Blueprint variable to `itupass/views/__init__.py` file for easy import.
* Register your view in `itupass/itupass.py` file to make it accessible.

**Conclusion**:

* After adding Model, Form, View and Template for that view, registering Blueprint for that view in `DEFAULT_BLUEPRINTS` variable, your new item will be added to the app.
* There are 2 main view, `client`, `dashboard` and `admin`, which is for main control. Most of the models will use only these views to show themself instead of own views.
