# -*- coding: utf-8 -*-
from syrinx import app
from syrinx.utils.security import generate_password_hash
from syrinx.models.backends import BackendAdapter

from datetime import datetime
from flaskext.sqlalchemy import SQLAlchemy
from hashlib import sha512, md5


class User(object):
    """A user.
    """

    __metaclass__ = BackendAdapter

    def __init__(self, username=None, server=None, location=None,
                 profile_uri=None, created=None, *args, **kwargs):
        print('User.__init__')
        self.username = username
        self.server = server or app.config['SERVER_URI']
        self.location = location
        self.profile_uri = profile_uri
        self.created = created or datetime.now()

    def get_key(self):
        return '%(username)s@%(server)s' % {
            'username': self.username,
            'server': self.server}

    def __unicode__(self):
        return u'%(username)s@%(server)s' % {
            'username': self.username,
            'server': self.server}

    __str__ = __unicode__


class RemoteUser(User):
    """A remote user.
    """

    # Cuando quiero seguir un usuario en otro servidor, se me pregunta
    # usuario@servidor de mi cuenta, el servicio lo registra y lo guarda en una
    # cookie para futuros casos. Se tiene que dar la opción a eliminarlo.
    def __init__(self, profile_uri=None, name=None, *args, **kwargs):
        self.profile_uri = profile_uri  # URI del perfil del usuario remoto.
        self.name = name
        super(RemoteUser, self).__init__(*args, **kwargs)


class LocalUser(User):
    """A local user.
    """

    lists = []
    followers = {}
    following = {}
    notices = []
    private_notices = []

    def __init__(self, password=None, salt=None, first_name=None,
                 last_name=None, bio=None, status=None, email=None, web=None,
                 date_joined=None, user_config=None, admin_user=None,
                 twitter_user=None, *args, **kwargs):
        print('LocalUser.__init__')
        # kwargs.get('user') == [a-zA-z0-9_\-]
        self.password = password
        self.salt = salt or self.generate_salt()
        self.first_name = first_name
        self.last_name = last_name
        self.bio = bio
        self.status = status
        self.email = email
        self.web = web
        self.date_joined = date_joined or datetime.now()
        self.user_config = user_config
        self.admin_user = admin_user
        self.twitter_user = twitter_user
        # FIXME: When calling super it returns a LocalUser. Why? How can I make
        # sure it calls __init__ on User?
        super(LocalUser, self).__init__(*args, **kwargs)

    def add_list(self, ulist, *args, **kwargs):
        self.lists.append(ulist)

    def add_to_list(self, ulist, user, *args, **kwargs):
        ulist.add_member(user, *args, **kwargs)

    def follow(self, user, ulist=None, *args, **kwargs):
        self.following[user.get_key()] = user
        if ulist:
            self.add_to_list(user, ulist)

    def post_notice(self, notice, *args, **kwargs):
        self.notices.append(notice)

    def send_private_notice(self, notice, *args, **kwargs):
        self.private_notices.append(notice)

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        if value:
            self._password = generate_password_hash(value, method='sha256')

    def check_password(self, password):
        return self.password == generate_password_hash(password,
                                                       method='sha256')

    def generate_salt(self):
        return md5('%(now)s$%%&%(secret)s' % {
            'now': str(datetime.now()),
            'secret': app.config['SECRET_KEY']}).hexdigest()


class UserConfig(object):
    """A user configuration.
    """

    __metaclass__ = BackendAdapter

    def __init__(self, protected=False, email_notification=True,
                 *args, **kwargs):
        self.protected = protected
        self.email_notification = email_notification

    def __unicode__(self):
        return u"<UserConfig #%i>" % self.pk

    __str__ = __unicode__


class AdminUser(object):
    """An admin user.
    """

    __metaclass__ = BackendAdapter

    def __init__(self, is_root=False, *args, **kwargs):
        self.is_root = is_root

    def __unicode__(self):
        return u"<AdminUser '%s'>" % self.user.__unicode__()

    __str__ = __unicode__


class TwitterUser(object):
    """A twitter user.
    """

    __metaclass__ = BackendAdapter

    def __init__(self, username, password, *args, **kwargs):
        self.username = username
        self.password = password

    def __unicode__(self):
        return self.username

    __str__ = __unicode__


class UserList(object):
    """A list of people I'm following.
    """

    __metaclass__ = BackendAdapter

    def __init__(self, name, members={}, muted=False, created=None,
                 *args, **kwargs):
        self.name = name
        self.members = members  # BackendDict(members)
        self.muted = muted
        self.created = created

    def add_member(self, user, *args, **kwargs):
        self.members[user.get_key()] = user

    def __unicode__(self):
        return self.name

    __str__ = __unicode__


class Notice(object):
    """A notice.
    """

    __metaclass__ = BackendAdapter

    def __init__(self, content=None, repeats=None,
                 date_publish=None, *args, **kwargs):
        self.content = content
        self.repeats = repeats  # Notice
        self.date_publish = date_publish or datetime.now()

    def __unicode__(self):
        return self.content

    __str__ = __unicode__


class PrivateNotice(object):
    """A private notice.
    """

    __metaclass__ = BackendAdapter

    def __init__(self, recipient, read=False, *args, **kwargs):
        self.recipient = recipient
        self.read = read

    def __unicode__(self):
        return self.content

    __str__ = __unicode__
