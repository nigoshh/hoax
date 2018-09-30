from flask_wtf import FlaskForm
from wtforms import (PasswordField, StringField, SubmitField,
                     validators)
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from application.utils import form_utils
from application.communities.models import Community

ln = validators.Length
rq = validators.InputRequired
eq = validators.EqualTo
ln_if_p = form_utils.length_if_present


def all_c():
    return Community.query.all()


class AccountFormCreate(FlaskForm):
    username = StringField("username", [rq(), ln(max=23)])
    community = QuerySelectField("community", [rq()], get_label="address",
                                 query_factory=all_c)
    password = PasswordField("password", [rq(), ln(min=9, max=52),
                             eq("repeat_pw", message="Passwords must match.")])
    repeat_pw = PasswordField("repeat password")
    apartment = StringField("apartment", [rq(), ln(max=13)])
    forename = StringField("forename", [rq(), ln(max=70)])
    surname = StringField("surname", [rq(), ln(max=70)])
    email = StringField("email address", [rq(), ln(max=65)])
    phone = StringField("phone", [rq(), ln(max=65)])
    submit = SubmitField("create account")

    class Meta:
        csrf = False


class AccountFormUpdate(FlaskForm):
    username = StringField("username", [ln(max=23)])
    community = QuerySelectField("community", get_label="address",
                                 query_factory=all_c)
    current_pw = PasswordField("current password", [rq()])
    password = PasswordField("new password", [ln_if_p(min=9, max=52),
                             eq("repeat_pw", message="Passwords must match.")])
    repeat_pw = PasswordField("repeat new password")
    apartment = StringField("apartment", [ln(max=13)])
    forename = StringField("forename", [ln(max=70)])
    surname = StringField("surname", [ln(max=70)])
    email = StringField("email address", [ln(max=65)])
    phone = StringField("phone", [ln(max=65)])
    submit = SubmitField("update account")

    class Meta:
        csrf = False