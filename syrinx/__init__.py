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
import sys

__version__ = '0.1.1'
__flask_version__ = '0.6.1'

try:
    from settings import *
except ImportError:
    # cp settings.py-customize settings.py
    logging.warning('Could not find local settings. Aborting...')
    sys.exit(1)

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
