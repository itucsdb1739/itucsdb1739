from flask import current_app
from collections import OrderedDict

def get_database():
    from itupass import get_db
    return get_db(current_app)


class Department(object):
    columns = OrderedDict([
        ('code', None),  # BLG, BLGE, TEL
        ('name', None)
    ])

    def __init__(self, code=None, name=None):
        for key in self.columns:
            setattr(self, key, vars().get(key))

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<Department {code}: {name}>'.format(code=self.code, name=self.name)

    def get_values(self):
        """Get values of object as dict object."""
        values = self.columns.copy()
        for key in self.columns:
            values[key] = getattr(self, key)
        return values

    def get_id(self):
        return str(self.code)

    @classmethod
    def get(cls, code=None):
        """Get department using identifier.

        :example: Department.get(code)
        :rtype: Department or None
        """
        db = get_database()
        cursor = db.cursor
        if code:
            cursor.execute(
                "SELECT * FROM {table} WHERE (code=%(code)s)".format(table=cls.Meta.table_name),
                {'code': code}
            )
        else:
            # @TODO raise exception, not enough arguments!
            return None
        department = db.fetch_execution(cursor)
        if department:
            return Department(**department[0])
        return None

    @classmethod
    def filter(cls, limit=10, order="code DESC", **kwargs):
        """Filter departments.

        :Example: Department.filter(name='Computer Engineering', limit=10)
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
        departments = db.fetch_execution(cursor)
        result = []
        for department in departments:
            result.append(Department(**department))
        return result

    def delete(self):
        """Delete current department.

        :Example: department.delete()
        """
        if not self.code:
            raise ValueError("Department is not saved yet.")
        db = get_database()
        cursor = db.cursor
        query = "DELETE FROM {table} WHERE code=%(code)s".format(table=self.Meta.table_name)
        cursor.execute(query, {'code': self.code})
        db.commit()

    def save(self):
        db = get_database()
        cursor = db.cursor
        data = self.get_values()
        department = None
        if self.code:
            department = self.get(code=self.code)
        if department:
            # update old department
            old_data = department.get_values()
            diffkeys = [key for key in data if data[key] != old_data[key]]
            if not diffkeys:
                # Nothing changed
                return department
            filters = {}
            for key in diffkeys:
                filters[key] = self.get_values()[key]
            query = "UPDATE {table} SET ".format(table=self.Meta.table_name)
            for key in filters:
                query += key + ' = %(' + key + ')s, '
            # Remove last comma
            query = query.rstrip(', ') + ' '
            # Add filter
            query += "WHERE code={code}".format(code=department.code)
            cursor.execute(query, filters)
            db.commit()
            # Return saved department
            return self.get(code=department.code)
        # new department
        query = "INSERT INTO {table} " \
                "(code, name) " \
                "VALUES" \
                "(%(code)s, %(name)s)".format(
                    table=self.Meta.table_name
                )
        cursor.execute(query, dict(data))
        db.commit()
        return self.get(code=data['code'])

    class Meta:
        table_name = 'departments'
