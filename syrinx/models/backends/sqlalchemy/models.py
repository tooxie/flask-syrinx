# -*- coding: utf-8 -*-
from syrinx import app

from flaskext.sqlalchemy import SQLAlchemy
from hashlib import sha512, md5

db = SQLAlchemy(app)


class User(db.Model):
    """A user.
    """

    __tablename__ = 'users'

    # Cuando quiero seguir un usuario en otro servidor, se me pregunta
    # usuario@servidor de mi cuenta, el servicio lo registra y lo guarda en una
    # cookie para futuros casos. Se tiene que dar la opción a eliminarlo.

    # id = db.Column(_(u'id'), db.Integer, primary_key=True)
    username = db.Column(db.String(64), primary_key=True, index=True)
    first_name = db.Column(db.String(64), nullable=True)
    last_name = db.Column(db.String(64), nullable=True)
    email = db.Column(db.String(64))
    server = db.Column(db.String(64), primary_key=True, index=True,
        nullable=True)
    password = db.Column(db.String(128), nullable=True)
    salt = db.Column(db.String(32), nullable=True)
    location = db.Column(db.String(64), nullable=True)
    web = db.Column(db.String(64), nullable=True)
    profile_uri = db.Column(db.String(64), nullable=True)
    is_root = db.Column(db.Boolean, default=False)
    date_joined = db.Column(db.DateTime, nullable=True)

    db.PrimaryKeyConstraint('username', 'server')
    db.UniqueConstraint('username', 'server', name='user_id')

    def __init__(self, username, server='', password=None, name='', email='',
                 location='', web='', profile_uri='', is_root=False,
                 date_joined=None, *args, **kwargs):
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
        self.date_joined = date_joined

    def __unicode__(self):
        if self.server:
            return u'%s@%s' % (self.username, self.server)
        return self.username

    __str__ = __unicode__


class Follower(db.Model):
    """A follower.
    """

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

    def __init__(self, who, whom, date_follow, *args, **kwargs):
        self.who = who
        self.whom = whom
        self.date_follow = date_follow

    def __unicode__(self):
        return unicode(self.who)

    __str__ = __unicode__


class Message(db.Model):
    """A message.
    """

    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.Integer, db.ForeignKey('users.username'))
    text = db.Column(db.UnicodeText)
    date_publish = db.Column(db.DateTime)

    @property
    def email(self):
        return User.query.get((self.author, '')).email

    def __init__(self, author, text, date_publish, *args, **kwargs):
        self.author = author
        self.text = text
        self.date_publish = date_publish

    def __unicode__(self):
        return unicode(self.text)

    __str__ = __unicode__
