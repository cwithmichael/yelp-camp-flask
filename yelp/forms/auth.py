from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
)
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()], id="username")
    password = PasswordField(
        "Password", validators=[DataRequired(), Length(min=3)], id="password"
    )


class RegisterForm(LoginForm):
    email = EmailField("Email", validators=[DataRequired()], id="email")
