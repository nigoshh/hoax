from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, validators

rq = validators.InputRequired


class LoginForm(FlaskForm):
    username = StringField("username", [rq()])
    password = PasswordField("password", [rq()])
    submit = SubmitField("log in")

    class Meta:
        csrf = False
