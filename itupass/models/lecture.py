from datetime import datetime
from flask import current_app
from collections import OrderedDict
from itupass.models import Department, User


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

    @property
    def schedule(self):
        if not self.pk:
            return None
        return LectureSchedule.filter(lecture=self.pk)

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
    def department_lectures(cls, department, limit=100):
        db = get_database()
        cursor = db.cursor
        cursor.execute(
            """SELECT lecture FROM lecture_departments WHERE department=%(department)s
            LIMIT {limit}""".format(limit=limit),
            {'department': department}
        )
        lectures = cursor.fetchall()
        result = []
        for lecture in lectures:
            result.append(Lecture.get(pk=lecture[0]))
        return result

    @classmethod
    def count(cls, **kwargs):
        """Get total number of lectures."""
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

    def get_schedules(self):
        if not self.pk:
            return None
        return LectureSchedule.filter(lecture=self.pk)

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
    def filter(cls, limit=10, offset=0, order="id DESC", **kwargs):
        """Filter lectures.

        :Example: Lecture.filter(year=2017, limit=10)
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
        lectures = db.fetch_execution(cursor)
        result = []
        for lecture in lectures:
            result.append(Lecture(**lecture))
        return result

    @classmethod
    def filter_wild(cls, code=None, name=None, limit=10, offset=0):
        """Wildcard search for code."""
        query_limit = None
        query_offset = None
        if limit:
            query_limit = limit
            del limit
        if offset:
            query_offset = offset
            del offset
        db = get_database()
        cursor = db.cursor
        if code:
            code = "%{code}%".format(code=code)
            query = "SELECT * FROM {table} WHERE code LIKE %(code)s".format(table=cls.Meta.table_name)
        elif name:
            name = "%{name}%".format(name=name)
            query = "SELECT * FROM {table} WHERE name LIKE %(name)s".format(table=cls.Meta.table_name)
        else:
            return None
        if query_limit:
            query += " LIMIT " + str(query_limit)
        if query_offset:
            query += " OFFSET " + str(query_offset)
        cursor.execute(query, {'code': code, 'name': name})
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


class LectureSchedule(object):
    columns = OrderedDict([
        ('pk', None),
        ('lecture', None),
        ('building', None),
        ('room', None),
        ('day_of_week', None),
        ('start_time', None),
        ('end_time', None)
    ])

    WEEK_DAYS = {
        'Pazartesi': 1,
        'Salı': 2,
        'Çarşamba': 3,
        'Perşembe': 4,
        'Cuma': 5,
        'Cumartesi': 6,
        'Pazar': 7
    }

    def __init__(self, pk=None, lecture=None, building=None, room=None, day_of_week=None,
                start_time=None, end_time=None):
        # Convert day_of_week to integer value
        if day_of_week is not None:
            if isinstance(day_of_week, str):
                if day_of_week in self.WEEK_DAYS:
                    day_of_week = self.WEEK_DAYS[day_of_week]
                else:
                    day_of_week = None
            elif isinstance(day_of_week, int):
                if day_of_week < 1 or day_of_week > 7:
                    day_of_week = None
            else:
                day_of_week = None
        # set default values
        for key in self.columns:
            setattr(self, key, vars().get(key))

    def __str__(self):
        return "Schedule on {start} for lecture {lecture}".format(start=self.start_time, lecture=self.lecture)

    def __repr__(self):
        return '<LectureSchedule {pk}: {lecture}>'.format(pk=self.pk, lecture=self.lecture)

    def get_values(self):
        """Get values of object as dict object."""
        values = self.columns.copy()
        for key in self.columns:
            values[key] = getattr(self, key)
        return values

    def get_id(self):
        return str(self.pk)

    def get_lecture(self):
        if not self.lecture:
            return None
        return Lecture.get(pk=self.lecture)

    @classmethod
    def get(cls, pk=None):
        """Get lecture schedule using identifier.

        :example: LectureSchedule.get(lecture_id)
        :rtype: LectureSchedule or None
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
        lecture_schedule = db.fetch_execution(cursor)
        if lecture_schedule:
            return LectureSchedule(**lecture_schedule[0])
        return None

    @classmethod
    def filter(cls, limit=10, offset=0, order="id DESC", **kwargs):
        """Filter lecture schedules.

        :Example: LectureSchedule.filter(lecture=<pk>)
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
        schedules = db.fetch_execution(cursor)
        result = []
        for schedule in schedules:
            result.append(LectureSchedule(**schedule))
        return result

    def delete(self):
        """Delete current lecture schedule.

        :Example: lecture_schedule.delete()
        """
        if not self.pk:
            raise ValueError("Lecture Schedule is not saved yet.")
        db = get_database()
        cursor = db.cursor
        query = "DELETE FROM {table} WHERE id=%(pk)s".format(table=self.Meta.table_name)
        cursor.execute(query, {'pk': self.pk})
        db.commit()

    def save(self):
        db = get_database()
        cursor = db.cursor
        data = self.get_values()
        schedule = None
        if self.pk:
            schedule = self.get(pk=self.pk)
        if schedule:
            # update old lecture schedule
            old_data = schedule.get_values()
            diffkeys = [key for key in data if data[key] != old_data[key]]
            if not diffkeys:
                # Nothing changed
                return schedule
            filters = {}
            for key in diffkeys:
                filters[key] = self.get_values()[key]
            query = "UPDATE {table} SET ".format(table=self.Meta.table_name)
            for key in filters:
                query += key + ' = %(' + key + ')s, '
            # Remove last comma
            query = query.rstrip(', ') + ' '
            # Add filter
            query += "WHERE id={pk}".format(pk=schedule.pk)
            cursor.execute(query, filters)
            db.commit()
            # Return saved schedule
            return self.get(pk=schedule.pk)
        # new lecture
        del data['pk']
        query = "INSERT INTO {table} " \
                "(lecture, building, room, day_of_week, start_time, end_time) " \
                "VALUES" \
                "(%(lecture)s, %(building)s, %(room)s, %(day_of_week)s, %(start_time)s, " \
                "%(end_time)s) RETURNING id".format(
                    table=self.Meta.table_name
                )
        cursor.execute(query, dict(data))
        db.commit()
        new_row_pk = cursor.fetchone()[0]
        return self.get(pk=new_row_pk)

    class Meta:
        table_name = 'lecture_schedule'


class UserLecture(object):
    columns = OrderedDict([
        ('pk', None),
        ('student', None),
        ('lecture', None),
        ('created_at', None)
    ])

    def __init__(self, pk=None, student=None, lecture=None, created_at=datetime.now()):
        for key in self.columns:
            setattr(self, key, vars().get(key))

    def __str__(self):
        return "Lecture {lecture} for {student}".format(lecture=self.lecture, student=self.student)

    def __repr__(self):
        return '<UserLecture {pk}>'.format(pk=self.pk)

    def get_values(self):
        """Get values of object as dict object."""
        values = self.columns.copy()
        for key in self.columns:
            values[key] = getattr(self, key)
        return values

    def get_id(self):
        return str(self.pk)

    @property
    def lecture_object(self):
        return Lecture.get(pk=self.lecture)

    @classmethod
    def count(cls, **kwargs):
        """Get total number of lecture registrations."""
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

    def get_schedules(self):
        if not self.lecture:
            return None
        return LectureSchedule.filter(lecture=self.lecture)

    @classmethod
    def get(cls, pk=None, student=None, lecture=None):
        """Get lecture registration using identifier.

        :example: user_lecture.get(registration_id)
        :rtype: UserLecture or None
        """
        db = get_database()
        cursor = db.cursor
        if pk:
            cursor.execute(
                "SELECT * FROM {table} WHERE (id=%(pk)s)".format(table=cls.Meta.table_name),
                {'pk': pk}
            )
        elif student and lecture:
            cursor.execute(
                "SELECT * FROM {table} WHERE (student=%(student)s and lecture=%(lecture)s)".format(
                    table=cls.Meta.table_name
                ), {'student': student, 'lecture': lecture}
            )
        else:
            # @TODO raise exception, not enough arguments!
            return None
        registration = db.fetch_execution(cursor)
        if registration:
            return UserLecture(**registration[0])
        return None

    @classmethod
    def filter(cls, limit=10, offset=0, order="id DESC", **kwargs):
        """Filter lecture registrations.

        :Example: user_lecture.filter(student=1, limit=10)
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
        registrations = db.fetch_execution(cursor)
        result = []
        for registration in registrations:
            result.append(UserLecture(**registration))
        return result

    def delete(self):
        """Delete current lecture registration.

        :Example: user_lecture.delete()
        """
        if not self.pk:
            raise ValueError("UserLecture is not saved yet.")
        db = get_database()
        cursor = db.cursor
        query = "DELETE FROM {table} WHERE id=%(pk)s".format(table=self.Meta.table_name)
        cursor.execute(query, {'pk': self.pk})
        db.commit()

    def save(self):
        db = get_database()
        cursor = db.cursor
        data = self.get_values()
        registration = None
        if self.pk:
            registration = self.get(pk=self.pk)
        if registration:
            # update old registration
            old_data = registration.get_values()
            diffkeys = [key for key in data if data[key] != old_data[key]]
            if not diffkeys:
                # Nothing changed
                return registration
            filters = {}
            for key in diffkeys:
                filters[key] = self.get_values()[key]
            query = "UPDATE {table} SET ".format(table=self.Meta.table_name)
            for key in filters:
                query += key + ' = %(' + key + ')s, '
            # Remove last comma
            query = query.rstrip(', ') + ' '
            # Add filter
            query += "WHERE id={pk}".format(pk=registration.pk)
            cursor.execute(query, filters)
            db.commit()
            # Return saved registration
            return self.get(pk=registration.pk)
        # new registration
        del data['pk']
        query = "INSERT INTO {table} " \
                "(student, lecture, created_at) " \
                "VALUES" \
                "(%(student)s, %(lecture)s, %(created_at)s) RETURNING id".format(
                    table=self.Meta.table_name
                )
        cursor.execute(query, dict(data))
        db.commit()
        new_row_pk = cursor.fetchone()[0]
        return self.get(pk=new_row_pk)

    class Meta:
        table_name = 'user_lectures'
