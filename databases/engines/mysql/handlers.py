try:
    import MySQLdb
    from MySQLdb import Error
except ImportError as e:
    from django.core.exceptions import ImproperlyConfigured
    raise ImproperlyConfigured("Error loading MySQLdb module: %s" % e)

from . import sql
from ...engines import (
    ENGINE_USER_NAME, ENGINE_USER_PASSWORD,
    DEFAULT_PORT, DEFAULT_HOST
)


def _get_existing_databases(cursor):
    """
    we need to pass a cursor (connection.cursor()) object to execute
    the query to the DB.

    This should ALWAYS be execute within an execution
    of a connection that closes both the cursor and the connection
    """
    databases = []
    cursor.execute("SHOW DATABASES")
    for db in cursor:
        databases.append(db[0])
    return databases


def _can_create_database(db_name, cursor):
    """
    Return True if we can proceed and create the new database, after
    checking that no other database with that name exist.

    we need to pass a cursor (connection.cursor()) object and pass it
    to the _get_existing_databases method

    This should ALWAYS be execute within an execution
    of a connection that closes both the cursor and the connection
    """
    databases = _get_existing_databases(cursor)
    if db_name not in databases:
        return True
    return False


def create_database(db_name, user_name=ENGINE_USER_NAME,
                    user_password=ENGINE_USER_PASSWORD,
                    host=DEFAULT_HOST, port=DEFAULT_PORT):
    """
    Establish a connection with the database engine
    next, we create a new database
    """
    connection_kwargs = {
        "host": host,
        "user": user_name,
        "passwd": user_password
    }
    if port:
        connection_kwargs["port"] = int(port)

    try:
        connection = MySQLdb.connect(**connection_kwargs)
        with connection.cursor() as cursor:
            if _can_create_database(db_name, cursor):
                sql.create_database(cursor, **{'db_name': db_name})
    except Error:
        raise
