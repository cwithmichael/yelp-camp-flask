from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, TextAreaField

class NewCampForm(FlaskForm):
    title = StringField('Title')
    location = StringField('Location')
    image = StringField('Image')
    description = TextAreaField('Description')
    price = DecimalField('Price')
