# -*- coding: utf-8 -*-
"""
This module provides decorators for the domain classes. These are not python
decorators but a design pattern that allows to attach additional
responsibilities to an object dynamically.

Decorators provide a flexible alternative to subclassing for extending
functionality.

Read more about this pattern: http://sourcemaking.com/design_patterns/decorator
"""

from syrinx.models.backends.utils import get_backend


class DecoratorBase(object):
    """A base decorator.
    """

    def __new__(cls, *args, **kwargs):
        pk = kwargs.get('pk')
        if pk:
            return get_backend().get(pk)
        self = object.__new__(cls)
        return self

    def save(self, backend=None):
        return get_backend(self, backend).save(self)

    def delete(self, backend=None):
        return get_backend(self, backend).delete(self)


class RemoteUserDecorator(DecoratorBase):

    pass


class LocalUserDecorator(DecoratorBase):
    """A local user backend mixin.
    """

    def add_list(self, instance, ulist, backend=None):
        return get_backend(self, backend).add_list(instance, ulist)

    def add_to_list(self, instance, who, ulist, backend=None):
        return get_backend(self, backend).add_to_list(instance, who, ulist)

    def follow(self, instance, who, backend=None):
        return get_backend(self, backend).follow(instance, who)

    def get_followers(self, instance, backend=None):
        return get_backend(self, backend).get_followers(instance)

    def post_notice(self, instance, notice, backend=None):
        return get_backend(self, backend).post_notice(instance, notice)

    def send_private_notice(self, instance, notice, backend=None):
        return get_backend(self, backend).send_private_notice(instance, notice)


class UserConfigDecorator(DecoratorBase):

    pass


class AdminUserDecorator(DecoratorBase):

    pass


class TwitterUserDecorator(DecoratorBase):

    pass


class UserListDecorator(DecoratorBase):

    pass


class NoticeDecorator(DecoratorBase):

    pass


class PrivateNoticeDecorator(DecoratorBase):

    pass
