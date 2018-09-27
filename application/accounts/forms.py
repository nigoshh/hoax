from flask_wtf import FlaskForm
from wtforms import (StringField, SelectField, PasswordField, SubmitField,
                     validators)
from application.utils import form_utils

ln = validators.Length
rq = validators.InputRequired
eq = validators.EqualTo
ln_if_p = form_utils.length_if_present


class AccountFormCreate(FlaskForm):
    username = StringField("username", [rq(), ln(max=23)])
    community_id = SelectField("community", coerce=int)
    password = PasswordField("password", [rq(), ln(min=9, max=52),
                             eq("repeat_pw", message="Passwords must match")])
    repeat_pw = PasswordField("repeat password")
    apartment = StringField("apartment", [rq(), ln(max=13)])
    forename = StringField("forename", [ln(max=70)])
    surname = StringField("surname", [ln(max=70)])
    email = StringField("email address", [ln(max=65)])
    phone = StringField("phone", [ln(max=65)])
    submit = SubmitField("create account")

    class Meta:
        csrf = False


class AccountFormUpdate(FlaskForm):
    username = StringField("username", [ln(max=23)])
    community_id = SelectField("community", coerce=int)
    old_pw = PasswordField("old password", [rq()])
    password = PasswordField("new password", [ln_if_p(min=9, max=52),
                             eq("repeat_pw", message="Passwords must match")])
    repeat_pw = PasswordField("repeat new password")
    apartment = StringField("apartment", [ln(max=13)])
    forename = StringField("forename", [ln(max=70)])
    surname = StringField("surname", [ln(max=70)])
    email = StringField("email address", [ln(max=65)])
    phone = StringField("phone", [ln(max=65)])
    submit = SubmitField("update account")

    class Meta:
        csrf = False
