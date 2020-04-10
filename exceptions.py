
__all__ = [
    'LolaInvalidAttribute',
]


class LolaError(Exception):
    """ Base exception for this module """
    pass


class LolaInvalidAttribute(LolaError):

    def __init__(self, attr):
        self.attribute = attr

    def __str__(self):
        return (
            'You are trying to check if %s exists in the settings.py '
            'module, but that is not a valid attribute' % self.attribute
        )

