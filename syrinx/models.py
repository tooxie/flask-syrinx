# -*- coding: utf-8 -*-
# from flaskext.babel import gettext as _
from flaskext.sqlalchemy import SQLAlchemy
from werkzeug import generate_password_hash
from hashlib import sha512, md5
from datetime import datetime
from syrinx import app
from os.path import abspath, dirname

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///%s/syrinx.db' % (
    dirname(abspath(__file__)))
db = SQLAlchemy(app)

class User(db.Model):

    __tablename__ = 'users'

    # Cuando quiero seguir un usuario en otro servidor, se me pregunta
    # usuario@servidor de mi cuenta, el servicio lo registra y lo guarda en una
    # cookie para futuros casos. Se tiene que dar la opción a eliminarlo.

    # id = db.Column(_(u'id'), db.Integer, primary_key=True)
    username = db.Column(db.String(64), primary_key=True, index=True)
    server = db.Column(db.String(64), primary_key=True, index=True,
        nullable=True)
    _password = db.Column(db.String(128), nullable=True)
    name = db.Column(db.String(64), nullable=True)
    email = db.Column(db.String(64))
    location = db.Column(db.String(64), nullable=True)
    web = db.Column(db.String(64), nullable=True)
    profile_uri = db.Column(db.String(64), nullable=True)
    is_root = db.Column(db.Boolean, default=False)
    date_joined = db.Column(db.DateTime, nullable=True)
    _salt = db.Column(db.String(32), nullable=True)

    db.PrimaryKeyConstraint('username', 'server')
    db.UniqueConstraint('username', 'server', name='user_id')

    def __init__(self, username, server='', password=None, name='', email='',
                 location='', web='', profile_uri='', is_root=False):
        # [a-zA-z0-9_\-]
        self.username = username
        self.server = server
        self.password = password
        self.name = name
        self.email = email
        self.location = location
        self.web = web
        self.profile_uri = profile_uri  # URI del perfil del usuario remoto.
        self.is_root = is_root
        self.date_joined = datetime.now()

    def __unicode__(self):
        if self.server:
            return '%s@%s' % (self.username, self.server)
        return self.username

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        if value:
            self._password = generate_password_hash(value)

    def check_password(self, password):
        return self.password == generate_password_hash(password)

    @property
    def salt(self):
        if self._salt:
            return self._salt
        self._salt = md5('%(now)s$%%&%(secret)s' % {
            'now': datetime.now(),
            'secret': app.config['SECRET_KEY']
        }).hexdigest()
        return self._salt

    @salt.setter
    def salt(self, value):
        pass  # ssshhh...


class Follower(db.Model):

    __tablename__ = 'followers'

    # id = db.Column(db.Integer, primary_key=True)
    who_id = db.Column(db.String, db.ForeignKey('users.username'),
        primary_key=True)
    whom_id = db.Column(db.String, db.ForeignKey('users.username'),
        primary_key=True)
    date_follow = db.Column(db.DateTime)

    who = db.relationship(User, backref=db.backref('followers'),
        primaryjoin='users.c.username==followers.c.who_id',
        order_by=date_follow)
    whom = db.relationship(User, backref=db.backref('following'),
        primaryjoin='users.c.username==followers.c.whom_id',
        order_by=date_follow)

    def __init__(self, who, whom):
        self.who = who
        self.whom = whom
        self.date_follow = datetime.now()


class Message(db.Model):

    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.Integer, db.ForeignKey('users.username'))
    text = db.Column(db.UnicodeText)
    date_publish = db.Column(db.DateTime)

    def __init__(self, author, text):
        self.author = author
        self.text = text
        self.date_publish = datetime.now()

    @property
    def email(self):
        return User.query.get((self.author, '')).email
