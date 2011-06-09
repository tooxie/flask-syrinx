# -*- coding: utf-8 -*-
"""
Tools for sending email.
"""

from syrinx import settings
from syrinx.core.exceptions import ImproperlyConfigured
from syrinx.core.mail.backends.smtp import EmailBackend as _SMTPConnection
from syrinx.core.mail.message import (BadHeaderError,
    DEFAULT_ATTACHMENT_MIME_TYPE, EmailMessage, EmailMultiAlternatives,
    forbid_multi_line_headers, make_msgid, SafeMIMEMultipart, SafeMIMEText,)
from syrinx.core.mail.utils import CachedDnsName, DNS_NAME
from syrinx.utils.importlib import import_module


def get_connection(backend=None, fail_silently=False, **kwargs):
    """Load an email backend and return an instance of it.

    If backend is None (default) settings.EMAIL_BACKEND is used.

    Both fail_silently and other keyword arguments are used in the
    constructor of the backend.
    """

    path = backend or settings.EMAIL_BACKEND
    try:
        mod_name, klass_name = path.rsplit('.', 1)
        mod = import_module(mod_name)
    except ImportError, e:
        raise ImproperlyConfigured(
            'Error importing email backend module %s: "%s"' % (mod_name, e))
    try:
        klass = getattr(mod, klass_name)
    except AttributeError:
        raise ImproperlyConfigured(
            'Module "%s" does not define a "%s" class' % (
                mod_name, klass_name))

    return klass(fail_silently=fail_silently, **kwargs)


def send_mail(subject, message, from_email, recipient_list,
              fail_silently=False, auth_user=None, auth_password=None,
              connection=None):
    """
    Easy wrapper for sending a single message to a recipient list. All members
    of the recipient list will see the other recipients in the 'To' field.

    If auth_user is None, the EMAIL_HOST_USER setting is used.
    If auth_password is None, the EMAIL_HOST_PASSWORD setting is used.

    Note: The API for this method is frozen. New code wanting to extend the
    functionality should use the EmailMessage class directly.
    """
    connection = connection or get_connection(username=auth_user,
                                    password=auth_password,
                                    fail_silently=fail_silently)
    return EmailMessage(subject=subject, body=message, from_email=from_email,
        to=recipient_list, connection=connection).send()


def send_mass_mail(datatuple, fail_silently=False, auth_user=None,
                   auth_password=None, connection=None):
    """
    Given a datatuple of (subject, message, from_email, recipient_list), sends
    each message to each recipient list. Returns the number of emails sent.

    If from_email is None, the DEFAULT_FROM_EMAIL setting is used.
    If auth_user and auth_password are set, they're used to log in.
    If auth_user is None, the EMAIL_HOST_USER setting is used.
    If auth_password is None, the EMAIL_HOST_PASSWORD setting is used.

    Note: The API for this method is frozen. New code wanting to extend the
    functionality should use the EmailMessage class directly.
    """
    connection = connection or get_connection(username=auth_user,
                                              password=auth_password,
                                              fail_silently=fail_silently)
    messages = [
        EmailMessage(subject=subject, body=message, from_email=sender,
                     to=[recipient])
        for subject, message, sender, recipient in datatuple]
    return connection.send_messages(messages)


def mail_admins(subject, message, fail_silently=False, connection=None,
                html_message=None):
    """Sends a message to the admins, as defined by the ADMINS setting."""
    if not settings.ADMINS:
        return
    mail = EmailMultiAlternatives(
        subject=unicode(''.join((settings.EMAIL_SUBJECT_PREFIX, subject))),
        body=message,
        from_email=settings.SERVER_EMAIL,
        to=[a[1] for a in settings.ADMINS],
        connection=connection)
    if html_message:
        mail.attach_alternative(html_message, 'text/html')
    mail.send(fail_silently=fail_silently)


def mail_managers(subject, message, fail_silently=False, connection=None,
                  html_message=None):
    """Sends a message to the managers, as defined by the MANAGERS setting."""
    if not settings.MANAGERS:
        return
    mail = EmailMultiAlternatives(
        subject=unicode(''.join((settings.EMAIL_SUBJECT_PREFIX, subject))),
        body=message,
        from_email=settings.SERVER_EMAIL,
        to=[a[1] for a in settings.MANAGERS],
        connection=connection)
    if html_message:
        mail.attach_alternative(html_message, 'text/html')
    mail.send(fail_silently=fail_silently)
