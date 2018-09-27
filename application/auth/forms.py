from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, validators

rq = validators.InputRequired


class LoginForm(FlaskForm):
    username = StringField("username", [rq()])
    password = PasswordField("password", [rq()])

    class Meta:
        csrf = False
