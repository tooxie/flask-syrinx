# -*- coding: utf-8 -*-
from syrinx.models.backends.utils import get_backend

# ---------------- #
#   Model mixins   #
# ---------------- #


class BackendMixin(object):
    """A backend mixin.
    """

    def __new__(cls, *args, **kwargs):
        pk = kwargs.get('pk')
        if pk:
            return BACKEND.get(pk)
        self = object.__new__(cls)
        return self

    def save(self, backend=None):
        return get_backend(self, backend).save(self)

    def delete(self, backend=None):
        return get_backend(self, backend).delete(self)


class UserBackendMixin(BackendMixin):

    pass


class RemoteUserBackendMixin(BackendMixin):

    pass


class LocalUserBackendMixin(BackendMixin):
    """A local user backend mixin.
    """

    def add_list(self, instance, ulist, backend=None):
        return get_backend(self, backend).add_list(instance, ulist)

    def add_to_list(self, instance, who, ulist, backend=None):
        return get_backend(self, backend).add_to_list(instance, who, ulist)

    def follow(self, instance, who, backend=None):
        return get_backend(self, backend).follow(instance, who)

    def get_followers(self, instance, backend=None):
        return get_backend(self, backend).get_followers(instance)

    def post_notice(self, instance, notice, backend=None):
        return get_backend(self, backend).post_notice(instance, notice)

    def send_private_notice(self, instance, notice, backend=None):
        return get_backend(self, backend).send_private_notice(instance, notice)


class UserConfigBackendMixin(BackendMixin):

    pass


class AdminUserBackendMixin(BackendMixin):

    pass


class TwitterUserBackendMixin(BackendMixin):

    pass


class UserListBackendMixin(BackendMixin):

    pass


class NoticeBackendMixin(BackendMixin):

    pass


class PrivateNoticeBackendMixin(BackendMixin):

    pass
