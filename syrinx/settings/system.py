# -*- coding: utf-8 -*-
"""
System-wide settings.
"""
from gettext import gettext as _
from os.path import abspath, dirname, join

PROJECT_DIR = dirname(abspath(__file__))[:-len('/settings')]

DEBUG = False

CONFIRMATION_EMAIL_SUBJECT = _('Confirm your email')
CONFIRMATION_EMAIL_TEMPLATE = 'confirmation.txt'
DEFAULT_CHARSET = 'utf-8'
EMAIL_BACKEND = 'syrinx.core.mail.backends.smtp.EmailBackend'
EMAIL_CONFIRMATION_TIMEOUT_DAYS = 3
EMAIL_PORT = 25
EMAIL_SUBJECT_PREFIX = '[Syrinx] '
EMAIL_USE_TLS = False
EMAIL_SIGNATURE_TEMPLATE = 'signature.txt'
MODEL_BACKEND = 'syrinx.models.backends.sqlalchemy'
SERVER_EMAIL = 'root@ideal.com.uy'
TEMPLATES_DIR = join(PROJECT_DIR, 'interface/www/templates')
