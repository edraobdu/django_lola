# -*- coding: utf-8 -*-

"""
This module will help use keep databases information secret

With get_databases we can call the dictionary of databases in
the settings file. And with insert_database we will update this }
dictionary, anytime we create a new client from the dev dashboard (using
'django_lola.py')
"""

import ast

from . import get_path_to_databases
from .exceptions import DatabaseExistsInDictionary


__author__ = "bezur"

__all__ = 'Databases'


class Databases(object):
    """
    This Class defines the map of the databases to be used by the system
    """

    def __init__(self, databases_path):
        self.databases_path = databases_path

    BACKENDS = {
        'mysql': 'django.db.backends.mysql',
        'postgres': 'django.db.backends.postgresql',
        'sqlite': 'django.db.backends.sqlite3'
    }

    DEFAULT_USER = 'bezur_bit2'
    DEFAULT_PASSWORD = 'COlombia-1864'
    DEFAULT_HOST = 'localhost'
    DEFAULT_PORT = ''
    DEFAULT_OPTIONS = {
        'init_command': 'SET foreign_key_checks = 0;'
    }

    @staticmethod
    def _check_string_parameter(parameter):
        """
        for some functions we need specifically a string as a parameter,
        or a number that can further be converted as string. So we do all the
        verifications an assertions in here
        """
        if not isinstance(parameter, (str, int, float)):
            raise TypeError(
                "parameter must be a string or number, "
                "you passed a %(type)s" % {
                    "type": type(parameter)
                }
            )
        return str(parameter)

    @staticmethod
    def pretty_dict(dictionary, level=1):
        """
        When we write a dictionary into a txt file, we end up with a single
        line, like: {'key': 'value', ...},

        For easy reading and understanding of the text file, we could write
        dictionaries on a better way, with indentation, like:
        {
            'key': 'value',
            ...
        }
        """

        def _nested(obj, nested_level=level):
            """
            Define an indented dictionary
            """
            indentation_values = "\t" * nested_level
            indentation_braces = "\t" * (nested_level - 1)
            if isinstance(obj, dict):
                return "{\n%(body)s%(indent_braces)s}" % {
                    "body": "".join("%(indent_values)s\'%(key)s\': %(value)s,\n" % {
                        "key": str(key),
                        "value": _nested(value, nested_level + 1),
                        "indent_values": indentation_values
                    } for key, value in obj.items()),
                    "indent_braces": indentation_braces
                }
            elif isinstance(obj, list):
                return "[\n%(body)s\n%(indent_braces)s]" % {
                    "body": "".join("%(indent_values)s%(value)s,\n" % {
                        "value": _nested(value, nested_level + 1),
                        "indent_values": indentation_values
                    } for value in obj),
                    "indent_braces": indentation_braces
                }
            else:
                return "\'%(value)s\'" % {"value": obj}

        return _nested(dictionary)

    def get_databases(self, file_obj=None, **kwargs):
        """
        return a new dictionary with the databases we want to display,
        if no db_list argument is passed, we retrieve all the
        databases' information, useful for constructing the settings DATABASES
        constant.

        We need to read the file databases.txt

        When we're inserting (or deleting or updating) a database, we have to
        read this file too, so we can specify that we alrady have a file object
        so we don't have to read the file again
        """
        db_list = kwargs.get('db_list')
        if file_obj:
            dbs = file_obj.read()
        else:
            try:
                with open(get_path_to_databases(), 'r+') as file_obj:
                    dbs = file_obj.read()
            except IOError:
                with open(get_path_to_databases(), 'w+') as file_obj:
                    # when starting, this database should be present
                    default_db = {
                        'default': {
                            'ENGINE': 'django.db.backends.mysql',
                            'NAME': self.set_db_name('Bit2'),
                            'PORT': '',
                            'HOST': 'localhost',
                            'USER': 'bezurnet_bit2',
                            'PASSWORD': 'COlombia-1864',
                            'OPTIONS': {
                                'init_command': 'SET foreign_key_checks = 0;',
                            },
                        }
                    }
                    file_obj.write(self.pretty_dict(default_db))
                    file_obj.seek(0)
                    dbs = file_obj.read()

        databases = ast.literal_eval(
            ' '.join(dbs.replace('\'', '"').split())
        )

        if db_list:
            if not isinstance(db_list, list):
                raise TypeError(
                    "db_list parameter must be a list of strings"
                )
            try:
                databases = {key: databases[key] for key in db_list}
            except (KeyError, TypeError, ValueError):
                # we pass and bring all the databases instead
                pass

        return databases

    def set_db_name(self, name):
        """
        Generates the name for the database for a specific user, 'default' is
        a reserved name for the 'bit2' app. We do not verify if this name is
        already taken in here, we do that in 'insert_database' function
        """
        name = self._check_string_parameter(name)
        assert str(name), "You must specify a name for the database"
        prefix = 'bezurnet'
        return "%(prefix)s_%(name)s" % {
            "name": name.lower(),
            "prefix": prefix
        }

    @classmethod
    def set_db_engine(cls, backend):
        """
        we obtain the engine backend for the new database
        """
        backend = cls._check_string_parameter(backend)
        assert str(
            backend), "You must specify a backend engine for the database"

        try:
            engine = cls.BACKENDS[backend]
        except KeyError:
            raise

        return engine

    @classmethod
    def set_db_user_name(cls, user=None, create=False):
        """
        generates the USER that is going to be managing the database
        If it does not exist in the database, it should be created and
        granted all privileges. If we don't pass any 'user', we get
        the DEFAULT_USER
        """
        db_user_name = cls.DEFAULT_USER
        if user:
            db_user_name = cls._check_string_parameter(user)
            if create:
                # todo - We can use django_lola to create the user in the database
                #  and grant all privileges to it
                pass
        return db_user_name

    @classmethod
    def set_db_user_password(cls, password=None):
        """
        generates the PASSWORD to be used by the user to access the
        database, If not password is passed we'll use the DEFAULT_PASSWORD
        """
        db_user_password = cls.DEFAULT_PASSWORD
        if password:
            db_user_password = cls._check_string_parameter(password)
        return db_user_password

    @classmethod
    def set_db_host(cls, host=None):
        """
        generates the HOST, if no host is passed, we'll use DEFAULT_HOST
        """
        db_host = cls.DEFAULT_HOST
        if host:
            db_host = cls._check_string_parameter(host)
        return db_host

    @classmethod
    def set_db_port(cls, port=None):
        """
        generates the PORT, if no host is passed, we'll use DEFAULT_PORT
        """
        db_port = cls.DEFAULT_PORT
        if port:
            db_port = cls._check_string_parameter(port)
        return db_port

    @classmethod
    def set_db_options(cls, options=None):
        """
        generates the OPTIONS for the database, if no host is passed,
        we'll use DEFAULT_OPTIONS
        """
        if not isinstance(options, dict):
            raise TypeError("Parameter 'options' must be a dictionary")
        db_options = cls.DEFAULT_OPTIONS
        if options:
            db_options = options
        return db_options

    @classmethod
    def _construct_database_dictionary(cls, name, engine, **kwargs):
        """
        Create the structure of the database dictionary

        kwargs:
            - user
            - password
            - host
            - port
            - options
        """
        user = kwargs.get('user')
        password = kwargs.get('password')
        host = kwargs.get('host')
        port = kwargs.get('port')
        options = kwargs.get('options')

        db_dictionary = {
            'ENGINE': cls.set_db_engine(engine),
            'NAME': cls.set_db_name(name),
            'USER': cls.set_db_user_name(user),
            'PASSWORD': cls.set_db_user_password(password),
            'HOST': cls.set_db_host(host),
            'PORT': cls.set_db_port(port)
        }

        if options:
            db_dictionary['OPTIONS'] = cls.set_db_options(options)

        return db_dictionary

    def insert_database_in_txt_file(self, name, engine, **kwargs):
        """
        Insert a new item into the dictionary of django_lola databases,
        here we check if the name of the databases already exists or not, if
        it does not, we can go ahead and insert it.
        """
        with open(get_path_to_databases(), 'r+') as file_obj:
            databases = self.get_databases(file_obj=file_obj)
            if name not in databases:
                new_db = self._construct_database_dictionary(
                    name=name,
                    engine=engine,
                    **kwargs
                )

                databases[name] = new_db
                file_obj.seek(0)
                file_obj.truncate()
                file_obj.write(self.pretty_dict(databases))

            else:
                raise DatabaseExistsInDictionary

    def __str__(self):
        return self.pretty_dict(self.get_databases())
