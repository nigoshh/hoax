from flask_wtf import FlaskForm
from wtforms import SubmitField, validators
from wtforms.fields.html5 import DateTimeField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from application.accounts.models import Account
from application.resources.models import Resource
from application.utils.form_utils import resource_label

opt = validators.Optional
rq = validators.InputRequired


class BookingFormCreate(FlaskForm):
    account = QuerySelectField("account", [rq()], get_label="username",
                               query_factory=Account.get_allowed_accounts)
    resource = QuerySelectField("resource", [rq()], get_label=resource_label,
                                query_factory=Resource.get_allowed_resources)
    start = DateTimeField("start", [rq()])
    end = DateTimeField("end", [rq()])
    submit = SubmitField("create booking")

    class Meta:
        csrf = False


class BookingFormUpdate(FlaskForm):
    account = QuerySelectField("account", get_label="username",
                               query_factory=Account.get_allowed_accounts)
    resource = QuerySelectField("resource", get_label=resource_label,
                                query_factory=Resource.get_allowed_resources)
    start = DateTimeField("start", [opt()])
    end = DateTimeField("end", [opt()])
    submit = SubmitField("update booking")

    class Meta:
        csrf = False
