import mongoengine as me
from yelp.models.review import Review
from yelp.models.user import User

def _not_empty(val):
    if not val:
        raise me.ValidationError("value can not be empty")


class Campground(me.Document):
    title = me.StringField(required=True, validation=_not_empty)
    image = me.StringField(required=True, validation=_not_empty)
    price = me.DecimalField(required=True, validation=_not_empty)
    description = me.StringField(required=True, validation=_not_empty)
    location = me.StringField(required=True, validation=_not_empty)
    reviews = me.ListField(me.ReferenceField(Review))
    author = me.ReferenceField(User)
