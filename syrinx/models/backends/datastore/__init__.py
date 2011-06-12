# -*- coding: utf-8 -*-
from syrinx.models.backends.base import BaseModelBackend

from google.appengine.ext import db


class ModelBackend(BaseModelBackend):

    pass


class UserBackend(ModelBackend):

    pass


class RemoteUserBackend(ModelBackend):

    pass


class LocalUserBackend(ModelBackend):

    pass


class UserConfigBackend(ModelBackend):

    pass


class AdminUserBackend(ModelBackend):

    pass


class TwitterUserBackend(ModelBackend):

    pass


class UserListBackend(ModelBackend):

    pass


class NoticeBackend(ModelBackend):

    pass


class PrivateNoticeBackend(ModelBackend):

    pass
