# -*- coding: utf-8 -*-
from syrinx.models.backends.base import BaseModelBackend


class ModelBackend(BaseModelBackend):
    """SQLAlchemy's model backend.
    """

    def get(self, cls, pk):
        raise NotImplementedError

    def save(self, instance):
        raise NotImplementedError

    def delete(self, instance):
        raise NotImplementedError


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
