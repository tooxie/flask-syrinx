# -*- coding: utf-8 -*-
from syrinx import app
from syrinx.models.backends.utils import get_backend


class BackendAdapter(type):
    """A metaclass to select at runtime whether to decorate the class or not.
    """

    def __new__(meta, cls, bases, dct):
        # If a backend is defined I wrap the object with a backend decorator.
        if app.config.get('MODEL_BACKEND', None):
            path_to_decorators = 'syrinx.models.backends.decorators'
            decorator_name = ''.join((cls, 'Decorator'))
            # Import the decorator
            wrapper = getattr(__import__(path_to_decorators, fromlist=['']),
                              decorator_name)
            # Create the instance of the domain-model which will then be used
            # as base class for the decorator.
            wrappee = type.__new__(meta, cls, bases, dct)
            # Return the wrapper.
            return type.__new__(meta, decorator_name, (wrappee,),
                                dict(wrapper.__dict__))
        # If there's no backend then continue as usual.
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
