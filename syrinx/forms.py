# -*- coding: utf-8 -*-
from flaskext.wtf import Form, TextField, Required, HiddenField


class FollowForm(Form):
    who = HiddenField('Who', validators=[Required()])
    # XXX: Validar que el account contenga arroba.
    account = TextField('Account', validators=[Required()])
