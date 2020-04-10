"""
In this file wi'll create all the structure of SQL sentences to use
by the engine, like for creating a database and insert a value in a
specific table

All of these actions should be execute after a connections was established,
so we must pass the cursor as a parameter
"""

__all__ = ['create_database']


def create_database(cursor, **params):
    """Create a new database"""
    db_name = params.get('db_name')
    assert isinstance(db_name, str)
    if db_name:
        sql = "CREATE DATABASE %(db_name)s"
        cursor.execute(sql, db_name)


