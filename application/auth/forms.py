from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, validators

ln = validators.Length
rq = validators.InputRequired


class LoginForm(FlaskForm):
    username = StringField("username", [rq(), ln(max=132)])
    password = PasswordField("password", [rq(), ln(max=132)])
    submit = SubmitField("log in")

    class Meta:
        csrf = False
