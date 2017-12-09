from flask import current_app
from flask_login import UserMixin
from collections import OrderedDict
from werkzeug.security import generate_password_hash, check_password_hash


def get_database():
    from itupass import get_db
    return get_db(current_app)


class User(UserMixin):
    """User Model."""
    columns = OrderedDict([
        ('pk', None),
        ('password', None),
        ('email', None),
        ('name', None),
        ('department', None),
        ('locale', 'en'),
        ('confirmed_at', None),
        ('deleted', False),
        ('is_teacher', False),
        ('is_staff', False)
    ])

    def __init__(self, pk=None, password=None, email=None, name=None, department=None,
                 locale='en', confirmed_at=None, deleted=False, is_teacher=False, is_staff=False):
        for key in self.columns:
            setattr(self, key, vars().get(key))
        if not self.pk and self.password:
            # new user
            self.set_password()

    def __str__(self):
        if self.name:
            return self.name
        return self.email

    def __repr__(self):
        return '<User {pk}: {email}>'.format(pk=self.pk, email=self.email)

    def set_password(self, password=None):
        """Make password hash."""
        if password:
            self.password = password
        self.password = generate_password_hash(self.password)

    def check_password(self, password):
        """Check password match with hash."""
        return check_password_hash(self.password, password)

    def get_values(self):
        """Get values of object as dict object."""
        values = self.columns.copy()
        for key in self.columns:
            values[key] = getattr(self, key)
        return values

    @property
    def is_active(self):
        return not self.deleted

    def get_id(self):
        return str(self.pk)

    @classmethod
    def count(cls, **kwargs):
        """Get total number of users."""
        db = get_database()
        filter_data = {}
        query = "SELECT count(id) FROM {table}".format(table=cls.Meta.table_name)
        # Add filters
        if kwargs:
            filter_query, filter_data = db.where_builder(kwargs)
            query += " WHERE " + filter_query
        cursor = db.cursor
        cursor.execute(query, filter_data)
        result = cursor.fetchall()
        if result:
            return result[0][0]
        return None

    @classmethod
    def get(cls, pk=None, email=None):
        """Get user using identifier.

        :example: User.get(user_id); User.get(email="some@domain.network")
        :rtype: User or None
        """
        db = get_database()
        cursor = db.cursor
        if pk:
            cursor.execute(
                "SELECT * FROM {table} WHERE (id=%(pk)s)".format(table=cls.Meta.table_name),
                {'pk': pk}
            )
        elif email:
            cursor.execute(
                "SELECT * FROM {table} WHERE (email=%(email)s)".format(table=cls.Meta.table_name),
                {'email': email}
            )
        else:
            # @TODO raise exception, not enough arguments!
            return None
        user = db.fetch_execution(cursor)
        if user:
            return User(**user[0])
        return None

    @classmethod
    def filter(cls, limit=10, offset=0, order="id DESC", **kwargs):
        """Filter users.

        :Example: User.filter(is_staff=True, limit=10) -> get list of 10 staff members
        :rtype: list
        """
        query_order = None
        query_limit = None
        query_offset = None
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
        if offset:
            query_offset = offset
            del offset
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
        if query_offset:
            query += " OFFSET " + str(query_offset)
        # Execute query and return result
        cursor.execute(query, filter_data)
        users = db.fetch_execution(cursor)
        result = []
        for user in users:
            result.append(User(**user))
        return result

    def disable(self):
        """Disable current user.

        :NOTE: Instead of deleting it will set deleted=true in user profile
        :Example: current_user.disable()
        """
        if not self.pk:
            raise ValueError("User is not saved yet.")
        db = get_database()
        cursor = db.cursor
        query = "UPDATE {table} SET deleted = TRUE WHERE id=%(id)s".format(table=self.Meta.table_name)
        cursor.execute(query, {'id': self.pk})
        db.commit()

    def delete(self):
        """Delete current user.

        :NOTE: This will only be used by admins
        :Example: current_user.delete()
        """
        if not self.pk:
            raise ValueError("User is not saved yet.")
        db = get_database()
        cursor = db.cursor
        query = "DELETE FROM {table} WHERE id=%(id)s".format(table=self.Meta.table_name)
        cursor.execute(query, {'id': self.pk})
        db.commit()

    def save(self):
        db = get_database()
        cursor = db.cursor
        data = self.get_values()
        user = self.get(email=self.email)
        if user:
            # update old user
            old_data = user.get_values()
            diffkeys = [key for key in data if data[key] != old_data[key]]
            if not diffkeys:
                # Nothing changed
                return user
            filters = {}
            for key in diffkeys:
                filters[key] = self.get_values()[key]
            query = "UPDATE {table} SET ".format(table=self.Meta.table_name)
            for key in filters:
                query += key + ' = %(' + key + ')s, '
            # Remove last comma
            query = query.rstrip(', ') + ' '
            # Add filter
            query += "WHERE id={pk}".format(pk=user.pk)
            cursor.execute(query, filters)
            db.commit()
            # Return saved user
            return self.get(pk=user.pk)
        # new user
        del data['pk']
        query = "INSERT INTO {table} " \
                "(email, name, department, locale, confirmed_at, is_teacher, is_staff, password) " \
                "VALUES" \
                "(%(email)s, %(name)s, %(department)s, %(locale)s, %(confirmed_at)s, %(is_teacher)s, " \
                "%(is_staff)s, %(password)s)".format(table=self.Meta.table_name)
        cursor.execute(query, dict(data))
        db.commit()
        return self.get(email=self.email)

    def __enter__(self):
        return self

    def __exit__(self, *kwargs):
        self.save()

    class Meta:
        table_name = 'users'
