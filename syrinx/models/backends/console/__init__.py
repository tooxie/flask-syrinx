# -*- coding: utf-8 -*-
from syrinx.models.backends.base import BaseModelBackend


class ModelBackend(BaseModelBackend):
    """Console model backend.
    """

    def get(self, pk):
        print pk

    def get_followers(self, instance, pk=None):
        print instance
        if pk:
            print pk

    def save(self, instance):
        print instance

    def delete(self, instance):
        print instance

    def add_list(self, instance, ulist):
        print instance

    def add_to_list(self, instance, ulist, user):
        print instance

    def follow(self, instance, user, ulist=None):
        print instance

    def contains(self, instance, key):
        print instance

    def delitem(self, instance, key):
        print instance

    def getitem(self, instance, key):
        print instance

    def setitem(self, instance, key, value):
        print instance

    def len(self, instance):
        print instance
        return 0

    def post_notice(self, instance, notice):
        print instance

    def send_private_notice(self, instance, notice):
        print instance

    def append(self, instance, item):
        print instance

    def add_member(self, instance, item):
        print instance
