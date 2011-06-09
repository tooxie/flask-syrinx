# -*- coding: utf-8 -*-
"""
Dummy email backend that does nothing.
"""

from syrinx.core.mail.backends.base import BaseEmailBackend


class EmailBackend(BaseEmailBackend):

    def send_messages(self, email_messages):
        return len(email_messages)
