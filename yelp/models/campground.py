import mongoengine as me

class Campground(me.Document):
    title = me.StringField()
    price = me.StringField()
    description = me.StringField()
    location = me.StringField()
    
    
