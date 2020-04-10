import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_path_to_databases():
    file_name = 'databases.txt'
    file_relative_path = ''.join(['databases/', file_name])
    return os.path.join(BASE_DIR, file_relative_path)
