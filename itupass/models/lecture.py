from datetime import datetime
from flask import current_app
from collections import OrderedDict
from itupass.models import Department


def get_database():
    from itupass import get_db
    return get_db(current_app)


class Lecture(object):
    columns = OrderedDict([
        ('pk', None),
        ('crn', None),
        ('code', None),  # BLG 361E
        ('name', None),
        ('instructor', None),
        ('year', None)
    ])

    def __init__(self, pk=None, crn=None, code=None, name=None, instructor=None, year=datetime.now().year):
        for key in self.columns:
            setattr(self, key, vars().get(key))

    def __str__(self):
        return "{code}: {name}".format(code=self.code, name=self.name)

    def __repr__(self):
        return '<Lecture {pk}: {code}>'.format(pk=self.pk, code=self.code)

    def get_values(self):
        """Get values of object as dict object."""
        values = self.columns.copy()
        for key in self.columns:
            values[key] = getattr(self, key)
        return values

    def get_id(self):
        return str(self.pk)

    @property
    def departments(self):
        if not self.pk:
            return None
        db = get_database()
        cursor = db.cursor
        cursor.execute("SELECT department FROM lecture_departments WHERE lecture=%(pk)s", {'pk': self.pk})
        departments = db.fetch_execution(cursor)
        if not departments:
            return []
        result = []
        for department in departments:
            result.append(Department.get(code=department['department']))
        return result

    def add_department(self, department):
        if not isinstance(department, Department):
            department = Department.get(code=department)
        if not department:
            return False
        db = get_database()
        cursor = db.cursor
        cursor.execute(
            "INSERT INTO lecture_departments (lecture, department) VALUES (%(lecture)s, %(department)s)",
            {'lecture': self.pk, 'department': department.code}
        )
        db.commit()
        return True

    @classmethod
    def get(cls, pk=None):
        """Get lecture using identifier.

        :example: Lecture.get(lecture_id)
        :rtype: Lecture or None
        """
        db = get_database()
        cursor = db.cursor
        if pk:
            cursor.execute(
                "SELECT * FROM {table} WHERE (id=%(pk)s)".format(table=cls.Meta.table_name),
                {'pk': pk}
            )
        else:
            # @TODO raise exception, not enough arguments!
            return None
        lecture = db.fetch_execution(cursor)
        if lecture:
            return Lecture(**lecture[0])
        return None

    @classmethod
    def filter(cls, limit=10, order="id DESC", **kwargs):
        """Filter lectures.

        :Example: Lecture.filter(year=2017, limit=10)
        :rtype: list
        """
        query_order = None
        query_limit = None
        db = get_database()
        cursor = db.cursor
        filter_data = {}
        # Delete non-filter data
        if limit:
            query_limit = limit
            del limit
        if order:
            query_order = order
            del order
        # Select statement for query
        query = "SELECT * FROM " + cls.Meta.table_name
        # Add filters
        if kwargs:
            filter_query, filter_data = db.where_builder(kwargs)
            query += " WHERE " + filter_query
        # Add order and limit if set
        if query_order:
            query += " ORDER BY " + query_order
        if 'ASC' not in query_order and 'DESC' not in query_order:
            query += " DESC"
        if query_limit:
            query += " LIMIT " + str(query_limit)
        # Execute query and return result
        cursor.execute(query, filter_data)
        lectures = db.fetch_execution(cursor)
        result = []
        for lecture in lectures:
            result.append(Lecture(**lecture))
        return result

    @classmethod
    def filter_wild(cls, code=None, name=None, limit=10):
        """Wildcard search for code."""
        db = get_database()
        cursor = db.cursor
        if code:
            code = "%{code}%".format(code=code)
            cursor.execute(
                "SELECT * FROM {table} WHERE code LIKE %(code)s LIMIT {limit}".format(
                    table=cls.Meta.table_name, limit=limit
                ), {'code': code}
            )
        elif name:
            name = "%{name}%".format(name=name)
            cursor.execute(
                "SELECT * FROM {table} WHERE name LIKE %(name)s LIMIT {limit}".format(
                    table=cls.Meta.table_name, limit=limit
                ), {'name': name}
            )
        else:
            return None
        lectures = db.fetch_execution(cursor)
        result = []
        for lecture in lectures:
            result.append(Lecture(**lecture))
        return result

    def delete(self):
        """Delete current lecture.

        :Example: lecture.delete()
        """
        if not self.pk:
            raise ValueError("Lecture is not saved yet.")
        db = get_database()
        cursor = db.cursor
        query = "DELETE FROM {table} WHERE id=%(pk)s".format(table=self.Meta.table_name)
        cursor.execute(query, {'pk': self.pk})
        db.commit()

    def save(self):
        db = get_database()
        cursor = db.cursor
        data = self.get_values()
        lecture = None
        if self.pk:
            lecture = self.get(pk=self.pk)
        if lecture:
            # update old lecture
            old_data = lecture.get_values()
            diffkeys = [key for key in data if data[key] != old_data[key]]
            if not diffkeys:
                # Nothing changed
                return lecture
            filters = {}
            for key in diffkeys:
                filters[key] = self.get_values()[key]
            query = "UPDATE {table} SET ".format(table=self.Meta.table_name)
            for key in filters:
                query += key + ' = %(' + key + ')s, '
            # Remove last comma
            query = query.rstrip(', ') + ' '
            # Add filter
            query += "WHERE id={pk}".format(pk=lecture.pk)
            cursor.execute(query, filters)
            db.commit()
            # Return saved lecture
            return self.get(pk=lecture.pk)
        # new lecture
        del data['pk']
        query = "INSERT INTO {table} " \
                "(crn, code, name, instructor, year) " \
                "VALUES" \
                "(%(crn)s, %(code)s, %(name)s, %(instructor)s, %(year)s) RETURNING id".format(
                    table=self.Meta.table_name
                )
        cursor.execute(query, dict(data))
        db.commit()
        new_row_pk = cursor.fetchone()[0]
        return self.get(pk=new_row_pk)

    class Meta:
        table_name = 'lectures'