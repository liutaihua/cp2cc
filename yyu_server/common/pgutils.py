import itertools
import logging
import time
import psycopg2

from DBUtils.PooledDB import PooledDB

class Connection(object):
    def __init__(self, database, host, user, mincached=5, maxcached=10, maxshared=0):
        self.database = database
        self.host = host
        self.user = user
        self.mincached = mincached
        self.maxcached = maxcached
        self.maxshared = maxshared

        args = dict(
            database=database,
            user=user,
            mincached=mincached,
            maxcached=maxcached,
            maxshared=maxshared,
        )

        self.max_idle_time = 7 * 3600
        self._db = None
        self._db_args = args
        self._last_use_time = time.time()

        try:
            self.reconnect()
        except:
            logging.error("Cannot connect to postgres on %s", self.host,
                exc_info=True)

    def __del__(self):
        self.close()

    def close(self):
        if getattr(self, "_db", None) is not None:
            self._db.close()
            self._db = None

    def reconnect(self):
        """Closes the existing database connection and re-opens it."""
        self.close()
        self._db = PooledDB(psycopg2, **self._db_args).connection()


    def _ensure_connected(self):
        # PostgreSQL by default closes client connections that are idle for
        # 8 hours, but the client library does not report this fact until
        # you try to perform a query and it fails.  Protect against this
        # case by preemptively closing and reopening the connection
        # if it has been idle for too long (7 hours by default).
        if (self._db is None or
            (time.time() - self._last_use_time > self.max_idle_time)):
            self.reconnect()
            self._last_use_time = time.time()

    def _cursor(self):
        self._ensure_connected()
        return self._db.cursor()


    def _execute(self, cursor, query, parameters):
        try:
            cursor.execute(query, parameters)
            self._db.commit()
            return
        except OperationalError:
            logging.error("Error connecting to postgres on %s", self.host)
            self.close()
            raise

    def execute_lastrowid(self, query, parameters):
        """Executes the given query, returning the lastrowid from the query."""
        cursor = self._cursor()
        try:
            self._execute(cursor, query, parameters)
            return cursor.lastrowid
        finally:
            cursor.close()

    def execute_rowcount(self, query, parameters):
        """Executes the given query, returning the rowcount from the query."""
        cursor = self._cursor()
        try:
            self._execute(cursor, query, parameters)
            return cursor.rowcount
        finally:
            cursor.close()


    def executemany(self, query, parameters):
        """Executes the given query against all the given param sequences.

        We return the lastrowid from the query.
        """
        return self.executemany_lastrowid(query, parameters)

    def executemany_lastrowid(self, query, parameters):
        """Executes the given query against all the given param sequences.
        We return the lastrowid from the query.
        """
        cursor = self._cursor()
        try:
            cursor.executemany(query, parameters)
            return cursor.lastrowid
        finally:
            cursor.close()

    def executemany_rowcount(self, query, parameters):
        """Executes the given query against all the given param sequences.

        We return the rowcount from the query.
        """
        cursor = self._cursor()
        try:
            cursor.executemany(query, parameters)
            return cursor.rowcount
        finally:
            cursor.close()

    def query(self, query, parameters=[]):
        """Returns a row list for the given query and parameters."""
        cursor = self._cursor()
        try:
            self._execute(cursor, query, parameters)
            column_names = [d[0] for d in cursor.description]
            return [Row(itertools.izip(column_names, row)) for row in cursor]
        finally:
            cursor.close()

    def get(self, query, parameters=[]):
        """Returns the first row returned for the given query."""
        rows = self.query(query, parameters)
        if not rows:
            return None
        elif len(rows) > 1:
            raise Exception("Multiple rows returned for Database.get() query")
        else:
            return rows[0]

    def execute(self, query, parameters=[]):
        """Executes the given query, returning the lastrowid from the query."""
        return self.execute_lastrowid(query, parameters)


class Row(dict):
    """A dict that allows for object-like property access syntax."""

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)


OperationalError = psycopg2.OperationalError
