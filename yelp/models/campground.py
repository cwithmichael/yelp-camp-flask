import mongoengine as me

class Campground(me.Document):
    title = me.StringField()
    image = me.StringField()
    price = me.DecimalField()
    description = me.StringField()
    location = me.StringField()
    
    
