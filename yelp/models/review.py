import mongoengine as me
from yelp.models.user import User


def _not_empty(val):
    if not val:
        raise me.ValidationError("value can not be empty")


class Review(me.Document):
    body = me.StringField(required=True, validation=_not_empty)
    rating = me.IntField(required=True, validation=_not_empty)
    author = me.ReferenceField(User)
