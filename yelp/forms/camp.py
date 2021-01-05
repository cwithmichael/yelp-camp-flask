from flask_wtf import FlaskForm
from wtforms import StringField

class NewCampForm(FlaskForm):
    title = StringField('Title')
    location = StringField('Location')
