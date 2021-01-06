from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, TextAreaField
from wtforms.validators import DataRequired

class NewCampForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    image = StringField('Image', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    price = DecimalField('Price', validators=[DataRequired()])
