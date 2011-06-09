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
