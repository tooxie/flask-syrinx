# -*- coding: utf-8 -*-
from os.path import abspath, dirname

DEBUG = True
SECRET_KEY = '+EizlUhw+0dky2rEwRScXw2ji5tHuwv8BSP6N9NV18UwSiBQ8sOLNmlL5BRL7Cs='
PER_PAGE = 30
SERVER_URI = 'syrinx.tw'
# APP_NAME = 'syrinx'
SQLALCHEMY_DATABASE_URI = 'sqlite:///%s/syrinx.db' % (
    dirname(abspath(__file__)))
