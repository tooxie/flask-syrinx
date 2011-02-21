# -*- coding: utf-8 -*-
"""
Syrinx
======

A microblogging application written with Flask.
"""
from .exceptions import ConfigError
from datetime import datetime
from flask import Flask
from flaskext.script import Manager, Server
from hashlib import md5
import logging

# configuration
DEBUG = True
SECRET_KEY = '+EizlUhw+0dky2rEwRScXw2ji5tHuwv8BSP6N9NV18UwSiBQ8sOLNmlL5BRL7Cs='
PER_PAGE = 30
SERVER_URI = 'syrinx.tw'
# APP_NAME = 'syrinx'

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('SYRINX_SETTINGS', silent=True)

manager = Manager(app)
manager.add_command("runserver", Server())


def format_datetime(timestamp):
    """Format a timestamp for display."""
    return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d @ %H:%M')


def gravatar_url(email, size=80):
    """Return the gravatar image for the given email address."""
    return 'http://www.gravatar.com/avatar/%s?d=identicon&s=%d' % \
        (md5(email.strip().lower().encode('utf-8')).hexdigest(), size)

# add some filters to jinja
app.jinja_env.filters['datetimeformat'] = format_datetime
app.jinja_env.filters['gravatar'] = gravatar_url

import views
import models

if not app.config['SECRET_KEY']:
    logging.warning('Missing SECRET_KEY. Run utils.secret_key_gen() to ' + \
                    'generate one.')
