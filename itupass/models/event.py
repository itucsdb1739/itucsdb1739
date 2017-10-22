from flask import current_app
from collections import OrderedDict
from datetime import datetime


def get_database():
    from itupass import get_db
    return get_db(current_app)


class EventCategory(object):
    columns = OrderedDict([
        ('pk', None),
        ('slug', None),
        ('name', None),
        ('tr_name', None),
        ('ru_name', None)
    ])

    def __init__(self, pk=None, slug=None, name=None, tr_name=None, ru_name=None):
        for key in self.columns:
            setattr(self, key, vars().get(key))

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<EventCategory {pk}: {name}>'.format(pk=self.pk, name=self.name)

    def get_values(self):
        """Get values of object as dict object."""
        values = self.columns.copy()
        for key in self.columns:
            values[key] = getattr(self, key)
        return values

    def get_id(self):
        return str(self.pk)

    @classmethod
    def get(cls, pk=None, slug=None):
        """Get category using identifier.

        :example: EventCategory.get(category_id)
        :rtype: EventCategory or None
        """
        db = get_database()
        cursor = db.cursor
        if pk:
            cursor.execute(
                "SELECT * FROM {table} WHERE (id=%(pk)s)".format(table=cls.Meta.table_name),
                {'pk': pk}
            )
        elif slug:
            cursor.execute(
                "SELECT * FROM {table} WHERE (slug=%(slug)s)".format(table=cls.Meta.table_name),
                {'slug': slug}
            )
        else:
            # @TODO raise exception, not enough arguments!
            return None
        category = db.fetch_execution(cursor)
        if category:
            return EventCategory(**category[0])
        return None

    @classmethod
    def filter(cls, limit=10, order="id DESC", **kwargs):
        """Filter categories.

        :Example: EventCategory.filter(name='Test Category', limit=10)
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
        categories = db.fetch_execution(cursor)
        result = []
        for category in categories:
            result.append(EventCategory(**category))
        return result

    def delete(self):
        """Delete current category.

        :WARNING: Will delete all events in this category!
        :Example: category.delete()
        """
        if not self.pk:
            raise ValueError("Event Category is not saved yet.")
        db = get_database()
        cursor = db.cursor
        query = "DELETE FROM {table} WHERE id=%(id)s".format(table=self.Meta.table_name)
        cursor.execute(query, {'id': self.pk})
        db.commit()

    def save(self):
        db = get_database()
        cursor = db.cursor
        data = self.get_values()
        category = self.get(slug=self.slug)
        if category:
            # update old category
            old_data = category.get_values()
            diffkeys = [key for key in data if data[key] != old_data[key]]
            if not diffkeys:
                # Nothing changed
                return category
            filters = {}
            for key in diffkeys:
                filters[key] = self.get_values()[key]
            query = "UPDATE {table} SET ".format(table=self.Meta.table_name)
            for key in filters:
                query += key + ' = %(' + key + ')s, '
            # Remove last comma
            query = query.rstrip(', ') + ' '
            # Add filter
            query += "WHERE id={pk}".format(pk=category.pk)
            cursor.execute(query, filters)
            db.commit()
            # Return saved category
            return self.get(pk=category.pk)
        # new category
        del data['pk']
        query = "INSERT INTO {table} " \
                "(slug, name, tr_name, ru_name) " \
                "VALUES" \
                "(%(slug)s, %(name)s, %(tr_name)s, %(ru_name)s, %(is_teacher)s)".format(
                    table=self.Meta.table_name
                )
        cursor.execute(query, dict(data))
        db.commit()
        return self.get(slug=self.slug)

    def get_events(self, limit=10):
        """Get list of events in current category."""
        db = get_database()
        cursor = db.cursor
        cursor.execute(
            "SELECT * FROM {table} WHERE category=%(category)s".format(table=Event.Meta.table_name),
            {'category': self.pk}
        )
        events = db.fetch_execution(cursor)
        event_list = []
        for event in events:
            event_list.append(Event(**event))
        return event_list

    class Meta:
        table_name = 'event_categories'


class Event(object):
    """News, Announcements and etc."""
    columns = OrderedDict([
        ('pk', None),
        ('summary', None),
        ('date', None),
        ('category', None),
        ('url', None)
    ])

    def __init__(self, pk=None, summary=None, date=datetime.now(), category=None, url=None):
        for key in self.columns:
            setattr(self, key, vars().get(key))

    def __str__(self):
        return self.summary

    def __repr__(self):
        return '<Event {pk}: {name}>'.format(pk=self.pk, name=self.summary)

    def get_values(self):
        """Get values of object as dict object."""
        values = self.columns.copy()
        for key in self.columns:
            values[key] = getattr(self, key)
        return values

    def get_id(self):
        return str(self.pk)

    @classmethod
    def get(cls, pk=None):
        """Get event using identifier.

        :example: Event.get(event_id)
        :rtype: Event or None
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
        event = db.fetch_execution(cursor)
        if event:
            return Event(**event[0])
        return None

    @classmethod
    def filter(cls, limit=10, order="id DESC", **kwargs):
        """Filter events.

        :Example: Event.filter(summary='Test Event', limit=10)
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
        events = db.fetch_execution(cursor)
        result = []
        for event in events:
            result.append(Event(**event))
        return result

    def delete(self):
        """Delete current event.

        :Example: event.delete()
        """
        if not self.pk:
            raise ValueError("Event is not saved yet.")
        db = get_database()
        cursor = db.cursor
        query = "DELETE FROM {table} WHERE id=%(id)s".format(table=self.Meta.table_name)
        cursor.execute(query, {'id': self.pk})
        db.commit()

    def save(self):
        db = get_database()
        cursor = db.cursor
        data = self.get_values()
        event = None
        if self.pk:
            event = self.get(pk=self.pk)
        if event:
            # update old event
            old_data = event.get_values()
            diffkeys = [key for key in data if data[key] != old_data[key]]
            if not diffkeys:
                # Nothing changed
                return event
            filters = {}
            for key in diffkeys:
                filters[key] = self.get_values()[key]
            query = "UPDATE {table} SET ".format(table=self.Meta.table_name)
            for key in filters:
                query += key + ' = %(' + key + ')s, '
            # Remove last comma
            query = query.rstrip(', ') + ' '
            # Add filter
            query += "WHERE id={pk}".format(pk=event.pk)
            cursor.execute(query, filters)
            db.commit()
            # Return saved event
            return self.get(pk=event.pk)
        # new event
        del data['pk']
        query = "INSERT INTO {table} " \
                "(summary, date, category, url) " \
                "VALUES" \
                "(%(summary)s, %(date)s, %(category)s, %(url)s) RETURNING id".format(
                    table=self.Meta.table_name
                )
        cursor.execute(query, dict(data))
        db.commit()
        new_row_pk = cursor.fetchone()[0]
        return self.get(pk=new_row_pk)

    class Meta:
        table_name = 'events'
