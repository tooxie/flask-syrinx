# -*- coding: utf-8 -*-


class BaseModelBackend(object):
    """Base model backend.
    """

    def get(self, cls, pk):
        raise NotImplementedError

    def get_followers(self, instance, pk=None):
        raise NotImplementedError

    def add_list(self, instance, ulist):
        raise NotImplementedError

    def add_to_list(self, instance, ulist, user):
        raise NotImplementedError

    def follow(self, instance, user, ulist=None):
        raise NotImplementedError

    def save(self, instance):
        raise NotImplementedError

    def delete(self, instance):
        raise NotImplementedError

    def contains(self, instance, key):
        raise NotImplementedError

    def delitem(self, instance, key):
        raise NotImplementedError

    def getitem(self, instance, key):
        raise NotImplementedError

    def setitem(self, instance, key, value):
        raise NotImplementedError

    def len(self, instance):
        raise NotImplementedError

    def post_notice(self, instance, notice):
        raise NotImplementedError

    def send_private_notice(self, instance, notice):
        raise NotImplementedError

    def add_member(self, instance, item):
        raise NotImplementedError
