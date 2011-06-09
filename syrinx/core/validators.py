# -*- coding: utf-8 -*-
from syrinx.core.exceptions import ValidationError
from syrinx.utils.encoding import force_unicode

import re


class RegexValidator(object):

    regex = ''
    message = 'Enter a valid value.'
    code = 'invalid'

    def __init__(self, regex=None, message=None, code=None):
        if regex is not None:
            self.regex = regex
        if message is not None:
            self.message = message
        if code is not None:
            self.code = code

        if isinstance(self.regex, basestring):
            self.regex = re.compile(regex)

    def __call__(self, value):
        """
        Validates that the input matches the regular expression.
        """
        if not self.regex.search(force_unicode(value)):
            raise ValidationError(self.message, code=self.code)


class EmailValidator(RegexValidator):

    def __call__(self, value):
        try:
            super(EmailValidator, self).__call__(value)
        except ValidationError, e:
            # Trivial case failed. Try for possible IDN domain-part
            if value and u'@' in value:
                parts = value.split(u'@')
                domain_part = parts[-1]
                try:
                    parts[-1] = parts[-1].encode('idna')
                except UnicodeError:
                    raise e
                super(EmailValidator, self).__call__(u'@'.join(parts))
            else:
                raise

email_re = re.compile(
    r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"  # dot-atom
    r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-011\013\014\016-\177])*"'  # quoted-string
    r')@(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?$',
    re.IGNORECASE)  # domain
validate_email = EmailValidator(email_re, 'Enter a valid e-mail address.',
                                'invalid')

slug_re = re.compile(r'^[-\w]+$')
validate_slug = RegexValidator(slug_re, "Enter a valid 'slug' consisting of letters, numbers, underscores or hyphens.", 'invalid')

ipv4_re = re.compile(r'^(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}$')
validate_ipv4_address = RegexValidator(ipv4_re, 'Enter a valid IPv4 address.',
                                       'invalid')

comma_separated_int_list_re = re.compile('^[\d,]+$')
validate_comma_separated_integer_list = RegexValidator(comma_separated_int_list_re, 'Enter only digits separated by commas.', 'invalid')

mimetype_re = re.compile(r'^[\w]+\/[^\-]+[\w,\-,\d]+$')
validate_mimetype = RegexValidator(mimetype_re, 'Enter a valid mime-type',
                                   'invalid')

# Password must be between 5 and 8 chars, it must have at least 1 digit
password_re = re.compile(r'^(?=.*\d).{5,8}$')
validate_password = RegexValidator(password_re, 'Enter a valid password',
                                   'invalid')
