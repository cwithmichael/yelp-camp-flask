from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
)
from wtforms.fields.html5 import EmailField
from wtforms.validators import InputRequired, Length


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()], id="username")
    password = PasswordField(
        "Password", validators=[InputRequired(), Length(min=3)], id="password"
    )


class RegisterForm(LoginForm):
    email = EmailField("Email", validators=[InputRequired()], id="email")
