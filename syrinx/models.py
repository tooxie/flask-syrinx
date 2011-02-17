# -*- coding: utf-8 -*-
# from flaskext.babel import gettext as _
from flaskext.sqlalchemy import SQLAlchemy
from werkzeug import generate_password_hash
from hashlib import sha512, md5
from datetime import datetime
from . import app
from os.path import abspath, dirname

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///%s/syrinx.db' % (
    dirname(abspath(__file__)))
db = SQLAlchemy(app)

class User(db.Model):

    __tablename__ = 'users'

    # id = db.Column(_(u'id'), db.Integer, primary_key=True)
    username = db.Column(db.String(64), primary_key=True)
    _password = db.Column(db.String(128))
    email = db.Column(db.String(50))
    is_root = db.Column(db.Boolean)
    date_joined = db.Column(db.DateTime)
    _salt = db.Column(db.String(32))

    def __init__(self, username, password=None, email='', is_root=False):
        self.username = username
        self.password = password
        self.email = email
        self.is_root = is_root
        self.date_joined = datetime.now()

    def __unicode__(self):
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
        return User.query.get(self.author).email
