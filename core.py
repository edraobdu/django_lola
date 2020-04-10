"""
Herein we define the master class, the one that will handle databases
operations, console sentences and so on.
"""

import os

from django.conf import settings, LazySettings

from .databases.handlers import Databases
from .exceptions import *
from color_print import cprint


__all__ = ['Lola']


ENGINES = {
    "MYSQL": 'mysql',
    "POSTGRES": 'postgres',
    "SQLITE": 'sqlite',
}


# Strings that represents the name of the attribute that ww must
# look for in the settings module
SETTING_DATABASES = 'LOLA_DATABASES'
SETTING_SECRET_KEY = 'LOLA_SECRET_KEY'
SETTING_GIT = 'LOLA_GIT'

SETTINGS_ATTRIBUTES = [SETTING_DATABASES, SETTING_GIT, SETTING_SECRET_KEY]

# Lazy settings to retrieve basic information to store in Lola instances
lazy_settings = LazySettings()


def _get_hardcoded_secret_key():
    """ returns the secret key stored in settings.py """
    return lazy_settings.SECRET_KEY


def _get_hardcoded_databases():
    """ returns the hardcoded databases configuration in settings.py """
    return lazy_settings.DATABASES


def _get_base_dir():
    """
    Return the BASE_DIR value from the settings.py
    relative paths will be constructed on top of the BASE_DIR path.
    """
    return lazy_settings.BASE_DIR


def _join_path(endpoint, base_dir=None):
    """
    execute a joint between the base_dir path passed and the
    relative path if any
    """
    is_absolute = endpoint[0] == '/'
    if base_dir is None:
        base_dir = _get_base_dir()
    return os.path.join(base_dir, endpoint) if not is_absolute else endpoint


def _check_setting_attribute(attr):
    """
    Helper function that checks if an attribute exists in the settings.py
    module.
    """
    new_attr = None
    if attr in SETTINGS_ATTRIBUTES:
        if hasattr(lazy_settings, attr):
            new_attr = getattr(lazy_settings, attr)
            if attr == SETTING_GIT:
                # return the BASE_DIR by default
                cprint('INFO: Using git path different than project', 'bBU')
                cprint(
                    'You are using a root path for your git repository \n'
                    'different tha the project root.',
                    'bI'
                )
                new_attr = _get_base_dir()
        else:
            if attr == SETTING_DATABASES:
                cprint('WARNING: Missing Databases Path', 'yBU')
                cprint(
                    'You are using django_lola without specifying any path to store and\n'
                    'retrieve the databases information, this is not secure and we\n'
                    'encourage you to save your DATABASES configuration in a \n'
                    'separate text file.',
                    'yI'
                )
            elif attr == SETTING_SECRET_KEY:
                cprint('SECURITY RISK: Missing Secret Key Path', 'rBU')
                cprint(
                    'You are using django_lola without specifying any path to store and\n'
                    'retrieve the secret_key. It is extremely important that you\n'
                    'save this key in a text file where you can hide it from \n'
                    'malicious hackers',
                    'rI'
                )
            elif attr == SETTING_GIT:
                # return the BASE_DIR by default
                new_attr = _get_base_dir()
    else:
        raise LolaInvalidAttribute(attr)
    return new_attr


class Lola(object):

    def __init__(self, in_settings=False, setup=False, *args, **kwargs):
        # BASE_DIR
        self.base_dir = _get_base_dir()
        if setup:
            self.setup()
        else:
            # Verify the LOLA_* constants in the settings.
            self.databases_path = _check_setting_attribute(SETTING_DATABASES)
            self.secret_key_path = _check_setting_attribute(SETTING_SECRET_KEY)
            self.git_path = _check_setting_attribute(SETTING_GIT)

            # Helper databases handler
            self.databases = Databases(self.databases_path)

            # Optional initial engine, in case we're going to work with a specific
            # database engine
            self.engine = kwargs.get('engine', None)

            if in_settings:
                # If any other Lola instance try to use in_settings=True again
                # it will raise a RunTimeError because the 'settings' is
                # already configured
                settings.configure(**{
                    'DATABASES': self.get_databases(),
                    'SECRET_KEY': self.get_secret_key()
                })
            else:
                # We're not using any git command within the settings module
                pass

    def get_secret_key(self):
        """
        This must be called only when django_lola is instantiated within the
        settings.py module (and in_settings parameter set to True)
        """
        secret_key = ''
        if self.secret_key_path is not None:
            secret_key_absolute_path = _join_path(self.secret_key_path)
            try:
                with open(secret_key_absolute_path) as sk:
                    secret_key = sk.read().strip()
            except FileNotFoundError as e:
                cprint(
                    '%s. Then, you are using hardcoded SECRET_KEY value in\n'
                    'the settings.py module' % e, 'c')
        return secret_key

    def _create_database(self, db_name, **kwargs):
        """
        Establish a connection with the database engine,
        next, we create a new database

        db_name: name of the database
        kwargs:
            - host: str database host
            - port: int port of the database
            - user_name: str user to be used for creating the database
            - user_password: str password of the user
        """

        if self.engine == ENGINES['MYSQL']:
            from .databases.engines.mysql import handlers as mysql_handler
            mysql_handler.create_database(
                db_name=db_name,
                **kwargs
            )
        else:
            pass

    def get_databases(self):
        """
        Retrieve the dictionary of databases to be inserted in the
        settings constant DATABASES
        """
        return self.databases.get_databases()

    def create_database(self, name, **kwargs):
        """
        Create the database on the server, if it does not exist
        then, we insert it in the dictionary
        """
        self._create_database(
            db_name=self.databases.set_db_name(name),
        )

        self.databases.insert_database_in_txt_file(
            name=name,
            engine=self.engine,
            **kwargs
        )

    def setup(self):
        """
        Will create the required files to store the secret information of
        the project. We'll create a directory called 'lola_config' within the
        project root with all the required files with default information.
        Users can later move it to wherever they want and specified the paths
        in settings.py """

        # End Setting Lola Variables
        lola_settings = {
            'LOLA_SECRET_KEY': None,
            'LOLA_DATABASES': None,
            'LOLA_DB_USERS': None,
            'LOLA_GIT': None
        }

        cprint("Starting Lola configuration\n", 'bBH')

        # Asking for Confirmation
        continue_setup = False
        confirmation = ''
        while confirmation not in ['Y', 'y', 'N', 'n']:
            confirmation = input(
                "You're about to start the configuration for Lola. This will\n"
                "create some required files and folders within the project \n"
                "root, do you want to continue? (Y/n)"
            )
            if confirmation in ['Y', 'y']:
                continue_setup = True

        if continue_setup:

            #### CONTAINER FOLDER
            folder_exists = False
            folder_name = 'lola_config'
            cprint(
                "1) Creating a folder '%s/' within the project root path" % folder_name,
                'y'
            )
            while not folder_exists:
                main_folder_path = os.path.join(self.base_dir, folder_name)
                try:
                    os.mkdir(main_folder_path)
                except FileExistsError:
                    folder_name = input(
                        "A 'lola_config' folder already exists in %s. Please \n"
                        "choose another name for storing the files (Press 'q' to exit)" % self.base_dir)
                    if folder_name == 'q':
                        cprint('Bye!', 'mB')
                        exit()
                else:
                    folder_exists = True
            cprint("   Folder %s/ created successfully!!\n" % folder_name, 'bB')
            container_folder = os.path.join(self.base_dir, folder_name)

            ##### SECRET_KEY
            secret_key_file_name = 'secret_key.txt'
            cprint(
                "2) Creating a file '%s' within folder %s/" % (
                    secret_key_file_name,
                    folder_name
                ),
                'y'
            )
            secret_key = _get_hardcoded_secret_key()
            with open(os.path.join(container_folder, secret_key_file_name), 'w+') as sk:
                sk.write(secret_key)
                sk.seek(0)
            # Relative path to secret_key.txt file
            lola_settings['LOLA_SECRET_KEY'] = f'{folder_name}/{secret_key_file_name}'
            cprint("   File %s created successfully!!\n" % secret_key_file_name, 'bB')

            ##### DATABASES
            databases_file_name = 'databases.txt'
            cprint(
                "3) Creating a file '%s' within folder %s/" % (
                    databases_file_name,
                    folder_name
                ),
                'y'
            )
            databases = _get_hardcoded_databases()
            with open(os.path.join(container_folder, databases_file_name),
                      'w+') as db:
                db.write(Databases.pretty_dict(databases))
                db.seek(0)
            # Relative path to databases.txt file
            lola_settings['LOLA_DATABASES'] = f'{folder_name}/{databases_file_name}'
            cprint("   File %s created successfully!!\n" % databases_file_name, 'bB')

            ##### DATABASES USERS
            db_users_file_name = 'db_users.txt'
            cprint(
                "4) Creating a file '%s' within folder %s/" % (
                    db_users_file_name,
                    folder_name
                ),
                'y'
            )
            db_users = {
                'mysql': {
                    'name': '',
                    'password': '',
                    'host': '',
                    'port': ''
                },
                'postgres': {
                    'name': '',
                    'password': '',
                    'host': '',
                    'port': ''
                }
            }
            with open(os.path.join(container_folder, db_users_file_name), 'w+') as dbu:
                dbu.write(Databases.pretty_dict(db_users))
                dbu.seek(0)
            # Relative path to db_users.txt file
            lola_settings['LOLA_DB_USERS'] = f'{folder_name}/{db_users_file_name}'
            cprint("   File %s created successfully!!\n" % db_users_file_name, 'bB')

            #### RESULTS
            cprint("FINISH", 'H')
            cprint(
                "Great!! you just finished setting Lola up, now you have \n"
                "a '%(folder)s' folder within your project root directory with the \n"
                "following files inside:\n\n"
                "%(folder)s/\n"
                "--- %(secret_key)s\n"
                "--- %(databases)s\n"
                "--- %(db_users)s\n" % {
                    'folder': folder_name,
                    'secret_key': secret_key_file_name,
                    'databases': databases_file_name,
                    'db_users': db_users_file_name
                },
                'b'
            )

            #### NEXT STEP
            cprint("\nWHAT\'S NEXT?", 'cBU')
            cprint("Now add the following information to your settings.py:\n", 'c')
            cprint("# Import Lola", 'g')
            cprint("from django_lola import Lola\n", 'B')
            cprint(
                "# Add the LOLA_* attributes\n"
                "# If you have set some sort of 'local_setting.py' file \n"
                "# (which is highly recommended), make sure you set the LOLA_*\n"
                "# attributes before them in case you want to override them \n"
                "# when working locally", 'g'
            )
            cprint("\n".join("%(key)s = '%(value)s'" % {
                'key': key,
                'value': value
            } for key, value in lola_settings.items() if value is not None), 'B')
            cprint(
                "\n# Call Lola instance with 'in_settings' set to True\n"
                "# Place this ALWAYS at the bottom of the setting.py", 'g')
            cprint("Lola(in_settings=True)\n", 'B')
            cprint("# The main goal of django_lola is to keep your sensitive \n"
                   "information secure, that's why you need to remove the\n"
                   "SECRET_KEY and the DATABASES values from teh settings.py", 'g')
            cprint(
                "SECRET_KEY = \'look_elsewhere\'\n"
                "DATABASES = {}",
                'B')

        else:
            cprint("Bye!", 'mB')
            exit()


