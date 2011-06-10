# -*- coding: utf-8 -*-
from syrinx import settings
from syrinx.utils import importlib


def get_backend(backend=None, *args, **kwargs):
    if not backend:
        try:
            return BACKEND
        except NameError:
            pass
    if backend and callable(backend):
        return backend
    path = backend or settings.MODEL_BACKEND
    try:
        mod_name, klass_name = path.rsplit('.', 1)
        mod = importlib.import_module(mod_name)
    except ImportError, e:
        raise ImproperlyConfigured(
            'Error importing model backend module %s: "%s"' % (mod_name, e))
    try:
        klass = getattr(mod, klass_name)
    except AttributeError:
        raise ImproperlyConfigured(
            'Module "%s" does not define a "%s" class' % (
                mod_name, klass_name))

    return klass(*args, **kwargs)

BACKEND = get_backend(settings.MODEL_BACKEND)


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
        return get_backend(backend).save(self)

    def delete(self, backend=None):
        return get_backend(backend).delete(self)


class BackendListMixin(object):
    """A backend list mixin.
    """

    def add_member(self, instance, item, backend=None):
        return get_backend(backend).add_member(instance, item)


class FollowMixin(object):
    """Backend functionality for local users.
    """

    def add_list(self, instance, ulist, backend=None):
        return get_backend(backend).add_list(instance, ulist)

    def add_to_list(self, instance, who, ulist, backend=None):
        return get_backend(backend).add_to_list(instance, who, ulist)

    def follow(self, instance, who, backend=None):
        return get_backend(backend).follow(instance, who)

    def get_followers(self, instance, backend=None):
        return get_backend(backend).get_followers(instance)

    def post_notice(self, instance, notice, backend=None):
        return get_backend(backend).post_notice(instance, notice)

    def send_private_notice(self, instance, notice, backend=None):
        return get_backend(backend).send_private_notice(instance, notice)


class NoticeMixin(object):

    pass


class BackendDict(dict):
    """A collection of objects.
    """

    def __contains__(self, key, backend=None):
        return get_backend(backend).contains(self, key)

    def __delitem__(self, key, backend=None):
        return get_backend(backend).delitem(self, key)

    def __getitem__(self, key, backend=None):
        return get_backend(backend).getitem(self, key)

    def __len__(self, backend=None):
        return get_backend(backend).len(self)

    def __setitem__(self, key, value, backend=None):
        return get_backend(backend).setitem(self, key, value)


class BackendList(list):
    """A list of objects.
    """

    items = []

    def append(self, item, backend=None):
        return get_backend(backend).append(self, item)

    def __len__(self, backend=None):
        return get_backend(backend).len(self)
