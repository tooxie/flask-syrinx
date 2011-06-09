# -*- coding: utf-8 -*-
from syrinx import settings
from syrinx.utils import importlib


def get_backend(backend=None, *args, **kwargs):
    if not backend:
        try:
            return BACKEND
        except NameError:
            pass
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


class BackendDictMixin(dict):
    """A collection of objects.
    """

    def __init__(self, model, key=None, *args, **kwargs):
        self.model = model
        # TODO: Implementar las keys.
        # TODO: Las keys permiten agrupar bajo un 'namespace' una serie de
        # TODO: modelos.
        super(BackendDictMixin, self).__init__(*args, **kwargs)

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


class FollowMixin(BackendDictMixin):
    """A users-I-follow dictionary.
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


class FollowerDict(FollowerMixin):
    """A users-who-follow-me dictionary.
    """

    def add(self, item, backend=None):
        return get_backend(backend).add(self, item)

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


class FollowersMixin(object):
    """A followers mixin.
    """

    def get_followers(self, backend=None):
        return get_backend(backend).get_followers(self)
