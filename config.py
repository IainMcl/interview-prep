"""
Read the contents of the config.ini file
"""

import configparser

class Config(object):
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
    
    def __str__(self):
        return 'Config'
    
    def get(self, section, option):
        return self.config.get(section, option)
    
    def get_sections(self):
        return self.config.sections()
    
    def get_options(self, section):
        return self.config.options(section)
    
    def get_database_options(self):
        return self.config.options('database')


def get_database_config(c: Config) -> dict:
    return {
        'username': c.get('database', 'postgres_user'),
        'password': c.get('database', 'postgres_password'),
        'host': c.get('database', 'host'),
        'port': c.get('database', 'port'),
        'database': c.get('database', 'postgres_db')
    }
    