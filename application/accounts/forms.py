from flask_wtf import FlaskForm
from wtforms import (PasswordField, StringField, SubmitField,
                     validators)
from wtforms.ext.sqlalchemy.fields import (QuerySelectField,
                                           QuerySelectMultipleField)
from application.utils import form_utils
from application.communities.models import Community

em = validators.Email
eq = validators.EqualTo
ln = validators.Length
ln_if_p = form_utils.length_if_present
rq = validators.InputRequired


class AccountFormCreate(FlaskForm):
    username = StringField("username", [rq(), ln(max=23)])
    community = QuerySelectField("community", [rq()],
                                 query_factory=Community.get_all)
    password = PasswordField("password", [rq(), ln(min=9, max=52),
                             eq("repeat_pw", message="Passwords must match.")])
    repeat_pw = PasswordField("repeat password")
    apartment = StringField("apartment", [rq(), ln(max=13)])
    forename = StringField("forename", [rq(), ln(max=70)])
    surname = StringField("surname", [rq(), ln(max=70)])
    email = StringField("email address", [rq(), em(), ln(max=65)])
    phone = StringField("phone", [rq(), ln(max=65)])
    admin_communities = (
        QuerySelectMultipleField("administered communities",
                                 query_factory=Community.get_all))
    submit = SubmitField("create account")

    class Meta:
        csrf = False


class AccountFormUpdate(FlaskForm):
    username = StringField("username", [ln(max=23)])
    community = QuerySelectField("community", query_factory=Community.get_all)
    current_pw = PasswordField("current password", [rq()])
    password = PasswordField("new password", [ln_if_p(min=9, max=52),
                             eq("repeat_pw", message="Passwords must match.")])
    repeat_pw = PasswordField("repeat new password")
    apartment = StringField("apartment", [ln(max=13)])
    forename = StringField("forename", [ln(max=70)])
    surname = StringField("surname", [ln(max=70)])
    email = StringField("email address", [em(), ln(max=65)])
    phone = StringField("phone", [ln(max=65)])
    admin_communities = (
        QuerySelectMultipleField("administered communities",
                                 query_factory=Community.get_all))
    submit = SubmitField("update account")

    class Meta:
        csrf = False
