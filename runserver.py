# -*- coding: utf-8 -*-
from syrinx import app
from syrinx.models import db
from os import path

db_path = path.join(path.dirname(path.abspath(__file__)), 'syrinx/syrinx.db')
if not path.exists(db_path):
    db.create_all()

app.run(debug=True)
