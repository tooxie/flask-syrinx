# -*- coding: utf-8 -*-
"""
    Syrinx
    ~~~~~~

    A microblogging application written with Flask and sqlite3.
"""
from hashlib import md5
from datetime import datetime
from flask import Flask, g
from flaskext.script import Manager, Server


# configuration
DEBUG = True
# sha256(md5(str(random())).hexdigest() + str(datetime.now())).hexdigest()
SECRET_KEY = '64bda706bc018ea5ffffdd67dc58caf184600651eea4150abb2b8008bde59ae1'
PER_PAGE = 30
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


if __name__ == '__main__':
    app.run()
