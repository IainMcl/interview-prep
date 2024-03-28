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