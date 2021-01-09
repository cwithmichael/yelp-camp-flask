import mongoengine as me
from .review import Review


def _not_empty(val):
    if not val:
        raise me.ValidationError("value can not be empty")


class User(me.Document):
    email = me.StringField(required=True, unique=True, validation=_not_empty)
    username = me.StringField(required=True, unique=True, validation=_not_empty)
    password = me.StringField(required=True, validation=_not_empty)
