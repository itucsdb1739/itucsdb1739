"""Common Models."""


class Database(object):
    def __init__(self, connection, database="postgresql"):
        self.connection = connection
        if database == "postgresql":
            self.connection.set_session(autocommit=False)

    @property
    def cursor(self):
        # @TODO Consider using connection pooling
        return self.connection.cursor()

    def set(self, connection=None):
        self.connection = connection

    def commit(self):
        self.connection.commit()

    def execute(self, *args, **kwargs):
        self.cursor.execute(*args, **kwargs)

    @staticmethod
    def fetch_execution(cursor):
        """Get results as dictionary.

        After cursor.execute command call this method to get `fetchall`
        results as dictionary list with column names.
        """
        results = []
        items = cursor.fetchall()
        columns = [i[0] for i in cursor.description]
        for item in items:
            data = {}
            for i in range(len(columns)):
                if columns[i] == 'id':
                    data['pk'] = item[i]
                else:
                    data[columns[i]] = item[i]
            results.append(data)
        return results

    @staticmethod
    def where_builder(filters, case='AND'):
        """Build where part for query.

        Imported from dbConnect Module, https://github.com/mastizada/dbConnect/, MPLv2
        Read https://dbconnect.readthedocs.io for more details
        :param case: Use AND or OR cases for filters
        :param filters: dict filters for rows (where)
        :return: str update query and dict where data
        """
        query = ""
        where_data = {}
        for key in filters:
            if isinstance(filters[key], tuple):
                if len(filters[key]) == 3:
                    # Like (id_start, id_end, '<=>')
                    if '=' in filters[key][2]:
                        query += key + ' >= ' + \
                                 '%(where_start_' + key + ')s AND ' + key + \
                                 ' <= ' + '%(where_end_' + key + ')s ' + \
                                 case + ' '
                    else:
                        query += key + ' > ' + '%(where_start_' + key + \
                                 ')s AND ' + key + ' < ' + '%(where_end_' + \
                                 key + ')s ' + case + ' '
                    where_data['start_' + key] = filters[key][0]
                    where_data['end_' + key] = filters[key][1]
                elif len(filters[key]) == 2:
                    # Like (id_start, '>=')
                    if not filters[key][0]:
                        query += key + ' ' + filters[key][1] + ' ' + \
                                 'NULL ' + case + ' '
                    else:
                        query += key + ' ' + filters[key][1] + ' ' + \
                                 '%(where_' + key + ')s ' + case + ' '
                        where_data[key] = filters[key][0]
                else:
                    raise ValueError(
                        "Missing case param in filter: %s" % filters[key][0]
                    )
            elif isinstance(filters[key], bool):
                query += key + ' = ' + '%(where_' + key + ')s ' + case + ' '
                where_data['where_' + key] = str(filters[key]).lower()
            elif not filters[key] and not isinstance(filters[key], int):
                query += key + ' is NULL ' + case + ' '
            else:
                query += key + ' = ' + '%(where_' + key + ')s ' + case + ' '
                where_data['where_' + key] = filters[key]
        return query.rstrip(case + ' '), where_data

    def close(self):
        if self.connection:
            self.connection.close()


class Paginator(object):
    def __init__(self, current_page=1, total_pages=1):
        self.current_page = current_page
        self.total_pages = total_pages

    @property
    def has_previous(self):
        return self.current_page > 1

    @property
    def has_next(self):
        return self.current_page < self.total_pages

    @property
    def pages(self):
        return [x + 1 for x in range(self.total_pages)]
