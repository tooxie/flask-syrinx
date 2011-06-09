# -*- coding: utf-8 -*-


class BaseModelBackend(object):
    """Base model backend.
    """

    def get(self, cls, pk):
        raise NotImplementedError

    def get_followers(self, instance, pk=None):
        raise NotImplementedError

    def save(self, instance):
        raise NotImplementedError

    def delete(self, instance):
        raise NotImplementedError
