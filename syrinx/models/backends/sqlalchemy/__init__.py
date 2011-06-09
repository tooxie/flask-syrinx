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
