# -*- coding: utf-8 -*-
from os import urandom
from base64 import b64encode


def secret_key_gen(random_bytes=47):
    return b64encode(urandom(random_bytes)).decode()
