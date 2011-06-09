# -*- coding: utf-8 -*-
from syrinx.models.backends.base import BaseModelBackend


class ModelBackend(BaseModelBackend):
    """Dummy model backend.
    """

    def get(self, pk):
        pass

    def save(self, instance):
        pass

    def delete(self, instance):
        pass
