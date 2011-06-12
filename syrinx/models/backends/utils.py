# -*- coding: utf-8 -*-
from syrinx import app
from syrinx.core.exceptions import ImproperlyConfigured
from syrinx.utils import importlib


def get_backend(instance, backend=None, *args, **kwargs):
    mod_name = backend or app.config['MODEL_BACKEND']
    klass_name = instance.__class__.__name__ + 'Backend'
    if backend:
        if callable(backend):
            return backend
    try:
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
