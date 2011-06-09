# -*- coding: utf-8 -*-
"""
Syrinx
======

A microblogging application written with Flask.
"""
from syrinx.exceptions import ConfigError

from datetime import datetime
from flask import Flask
from flaskext.script import Manager, Server
import hashlib
import logging
import sys

__author__ = u'Alvaro Mouriño <alvaro@mourino.net>'
__flask_version__ = '0.6.1'
__version__ = '0.1.2'

try:
    from syrinx import settings
except ImportError:
    logging.error('ERROR: Could not find settings. Aborting...')
    sys.exit(1)

app = Flask(__name__)
app.config.from_object(settings)

manager = Manager(app)
manager.add_command("runserver", Server())

if app.config['DEBUG']:

    def init_db():
        raise NotImplementedError


def format_datetime(timestamp):
    """Format a timestamp for display."""
    return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d @ %H:%M')


def gravatar_url(email, size=80):
    """Return the gravatar image for the given email address."""
    return 'http://www.gravatar.com/avatar/%s?d=identicon&s=%d' % \
        (hashlib.md5(email.strip().lower().encode('utf-8')).hexdigest(), size)

# add some filters to jinja
app.jinja_env.filters['datetimeformat'] = format_datetime
app.jinja_env.filters['gravatar'] = gravatar_url

from syrinx import models

if not app.config['SECRET_KEY']:
    logging.warning(' '.join('Missing settings.SECRET_KEY. Run'
                             'utils.crypto.gen_secretkey() to generate one.'))
