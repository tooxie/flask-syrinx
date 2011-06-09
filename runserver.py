# -*- coding: utf-8 -*-
from syrinx import app
from syrinx.models import db

from os import path

db_path = path.join(path.dirname(path.abspath(__file__)), 'syrinx/syrinx.db')
if not path.exists(db_path):
    print(' * Database created: %s' % db_path)
    db.create_all()

if not app.config['SECRET_KEY']:
    raise ConfigError(''.join('Missing SECRET_KEY. Run syrinx.utils.',
                              'secret_key_gen() to generate one.'))

app.run(debug=True)
