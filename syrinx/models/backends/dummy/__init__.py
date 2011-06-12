# -*- coding: utf-8 -*-
from syrinx.models.backends.base import BaseModelBackend


class ModelBackend(BaseModelBackend):
    """Dummy model backend.
    """

    def get(self, cls, pk):
        pass

    def get_followers(self, instance, pk=None):
        pass

    def add_list(self, instance, ulist):
        pass

    def add_to_list(self, instance, ulist, user):
        pass

    def follow(self, instance, user, ulist=None):
        pass

    def save(self, instance):
        pass

    def delete(self, instance):
        pass

    def contains(self, instance, key):
        pass

    def delitem(self, instance, key):
        pass

    def getitem(self, instance, key):
        pass

    def setitem(self, instance, key, value):
        pass

    def len(self, instance):
        return 0

    def post_notice(self, instance, notice):
        pass

    def send_private_notice(self, instance, notice):
        pass

    def append(self, instance, item):
        pass

    def add_member(self, instance, item):
        pass
