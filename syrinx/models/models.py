# -*- coding: utf-8 -*-
from syrinx import app
from syrinx.models.backends import (BackendMixin, BackendDictMixin,
    FollowerMixin, FollowMixin,)
from syrinx.utils.security import generate_password_hash

from datetime import datetime
from flaskext.sqlalchemy import SQLAlchemy
from hashlib import sha512, md5


# DEPRECATED
class FollowerDict(FollowerMixin):
    """A users-who-follow-me dictionary.
    """

    def __init__(self, users=[], *args, **kwargs):
        self.model = User
        for user in users:
            self.add(user)
        super(UserDict, self).__init__(*args, **kwargs)


class FollowDict(FollowMixin):
    """A users-I-follow dictionary.
    """

    def __init__(self, users=[], *args, **kwargs):
        self.model = User
        for user in users:
            self.add(user)
        super(UserDict, self).__init__(*args, **kwargs)


class ListMemberDict(ListMemberMixin):
    """A users dictionary.
    """

    def __init__(self, members=[], *args, **kwargs):
        self.model = User
        for member in members:
            self.add(member)
        super(UserDict, self).__init__(*args, **kwargs)


class NoticeDict(NoticeMixin):
    """A notices dictionary.
    """

    pass


class PrivateNoticeDict(PrivateNoticeMixin):
    """A notices dictionary.
    """

    pass
# /DEPRECATED


class NamespacedDict(BackendDictMixin):
    """A custom dictionary with namespace.
    """

    def __init__(self, model, ns, items=[], *args, **kwargs):
        self.model = model
        for item in items:
            self.add(item)
        super(NamespacedDict, self).__init__(ns, *args, **kwargs)


class User(BackendMixin):
    """A user.
    """

    FOLLOWERS = 'followers'
    FOLLOWING = 'following'

    def __init__(self, username=None, server=None, location=None,
                 profile_uri=None, created=None, *args, **kwargs):
        self.username = username
        self.server = server or app.config['SERVER_URI']
        self.location = location
        self.profile_uri = profile_uri
        self.created = created or datetime.now()
        super(User, self).__init__(*args, **kwargs)

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
    def __init__(self, server, profile_uri=None, name=None, *args, **kwargs):
        self.server = server
        self.profile_uri = profile_uri  # URI del perfil del usuario remoto.
        self.name = name
        super(RemoteUser, self).__init__(*args, **kwargs)


class LocalUser(User):
    """A local user.

    >>> user = LocalUser(pk=1)
    >>> follower = user.followers.get(pk=3)
    """

    def __init__(self, password=None, salt=None, first_name=None,
                 last_name=None, bio=None, status=None, email=None, web=None,
                 followers=[], following=[], notices=[], private_notices=[],
                 date_joined=None, user_config=None, admin_user=None,
                 twitter_user=None, *args, **kwargs):
        # kwargs.get('user') == [a-zA-z0-9_\-]
        self.password = password
        self.salt = salt or self.generate_salt()
        self.first_name = first_name
        self.last_name = last_name
        self.bio = bio
        self.status = status
        self.email = email
        self.web = web
        self.followers = NamespacedDict(model=User, ns=User.FOLLOWERS,
                                        items=followers)
        self.following = NamespacedDict(model=User, ns=User.FOLLOWING,
                                        items=following)
        self.notices = NamespacedDict(model=Notice, ns='Notice', items=notices)
        self.private_notices = NamespacedDict(model=PrivateNotice,
                                              ns='PrivateNotice',
                                              items=private_notices)
        self.date_joined = date_joined or datetime.now()
        self.user_config = user_config
        self.admin_user = admin_user
        self.twitter_user = twitter_user
        super(LocalUser, self).__init__(*args, **kwargs)

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


class UserConfig(BackendMixin):
    """A user configuration.
    """

    def __init__(self, protected=False, email_notification=True,
                 *args, **kwargs):
        self.protected = protected
        self.email_notification = email_notification
        super(UserConfig, self).__init__(*args, **kwargs)

    def __unicode__(self):
        return u"<UserConfig #%i>" % self.pk

    __str__ = __unicode__


class AdminUser(BackendMixin):
    """An admin user.
    """

    def __init__(self, user, is_root=False, *args, **kwargs):
        self.user = user
        self.is_root = is_root
        super(AdminUser, self).__init__(*args, **kwargs)

    def __unicode__(self):
        return u"<AdminUser '%s'>" % self.user.__unicode__()

    __str__ = __unicode__


class TwitterUser(BackendMixin):
    """A twitter user.
    """

    def __init__(self, username, password, *args, **kwargs):
        self.username = username
        self.password = password
        super(TwitterUser, self).__init__(*args, **kwargs)

    def __unicode__(self):
        return self.username

    __str__ = __unicode__


class Follower(BackendMixin):
    """A follower.
    """

    def __init__(self, who, *args, **kwargs):
        self.who = who
        self.date_follow = datetime.now()
        super(Follower, self).__init__(*args, **kwargs)

    def __unicode__(self):
        return u"<Follower '%s'>" % self.who.__unicode__()

    __str__ = __unicode__


class Followee(BackendMixin):
    """A followee.
    """

    def __init__(self, who, *args, **kwargs):
        self.who = who
        self.date_follow = datetime.now()
        super(Followee, self).__init__(*args, **kwargs)

    def __unicode__(self):
        return u"<Followee '%s'>" % self.who.__unicode__()

    __str__ = __unicode__


class List(BackendMixin):
    """A list of people I'm following.
    """

    def __init__(self, name, members=[], muted=False, created=None,
                 *args, **kwargs):
        self.name = name
        self.members = ListMemberDict(members)
        self.muted = muted
        self.created = created
        super(List, self).__init__(*args, **kwargs)

    def __unicode__(self):
        return self.name

    __str__ = __unicode__


class Notice(BackendMixin):
    """A notice.
    """

    def __init__(self, content=None, repeats=None,
                 date_publish=None, *args, **kwargs):
        self.content = content
        self.repeats = repeats  # Notice
        self.date_publish = date_publish or datetime.now()
        super(Notice, self).__init__(*args, **kwargs)

    def __unicode__(self):
        return self.content

    __str__ = __unicode__


class PrivateNotice(Notice):
    """A private notice.
    """

    def __init__(self, recipient, read=False, *args, **kwargs):
        self.recipient = recipient
        self.read = read
        super(PrivateNotice, self).__init__(*args, **kwargs)

    def __unicode__(self):
        return self.content

    __str__ = __unicode__
