"""
Create exceptions for the specific uses case  of creating new databases
"""
from . import get_path_to_databases

__author__ = "Bezur"

__all__ = ['DatabaseExistsInDictionary']


class DatabaseExistsInDictionary(Exception):

    def __init__(self, *args):
        self.message = self._get_message(
            message=args[0] if args else None
        )

    @classmethod
    def _get_message(cls, message=None):
        if message:
            return message
        else:
            return "The database that you're trying to create already " \
                   "exists in the dictionary of databases"

    def __str__(self):
        return self.message
