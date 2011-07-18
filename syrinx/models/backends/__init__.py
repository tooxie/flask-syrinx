# -*- coding: utf-8 -*-
from syrinx import app
from syrinx.models.backends.utils import get_backend


class BackendAdapter(type):
    """A metaclass to select at runtime whether to decorate the class or not.
    """

    def __new__(meta, cls, bases, dct):
        # If a backend is defined wrap the object with a backend decorator.
        if app.config.get('MODEL_BACKEND', None):
            path_to_decorators = 'syrinx.models.backends.decorators'
            decorator_name = ''.join((cls, 'Decorator'))
            # Import the decorator.
            wrapper = getattr(__import__(path_to_decorators, fromlist=['']),
                              decorator_name)
            # Apply backend-specific methods and properties.
            for attr in dir(wrapper):
                if not attr.startswith('__'):
                    _attr = getattr(wrapper, attr)
                    if hasattr(_attr, '__func__'):
                        dct[attr] = _attr.__func__
                    else:
                        dct[attr] = _attr
        # Return the object.
        return type.__new__(meta, cls, bases, dct)


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
