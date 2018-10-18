from flask_wtf import FlaskForm
from wtforms import BooleanField, SubmitField, validators
from wtforms.fields.html5 import DateField, TimeField
from wtforms.ext.sqlalchemy.fields import (QuerySelectField,
                                           QuerySelectMultipleField)
from application.accounts.models import Account
from application.resources.models import Resource

opt = validators.Optional
rq = validators.InputRequired


class BookingFormCreate(FlaskForm):
    account = QuerySelectField("account (in charge)", [rq()],
                               query_factory=Account.get_allowed)
    resource = QuerySelectField("resource", [rq()],
                                query_factory=Resource.get_allowed)
    start_date = DateField("starting date", [rq()])
    start_time = TimeField("starting time", [rq()])
    end_date = DateField("ending date", [rq()])
    end_time = TimeField("ending time", [rq()])
    submit = SubmitField("create booking")

    class Meta:
        csrf = False


class BookingFormFilter(FlaskForm):
    from_date = DateField("from (date)", [opt()])
    from_time = TimeField("from (time)", [opt()])
    to_date = DateField("to (date)", [opt()])
    to_time = TimeField("to (time)", [opt()])
    resources = QuerySelectMultipleField("resources",
                                         query_factory=Resource.get_allowed)
    filter_not_in_invoice = (
        BooleanField("show only bookings which are not in an invoice"))

    class Meta:
        csrf = False


class BookingFormUpdate(FlaskForm):
    account = QuerySelectField("account (in charge)",
                               query_factory=Account.get_allowed)
    resource = QuerySelectField("resource",
                                query_factory=Resource.get_allowed)
    start_date = DateField("starting date", [rq()])
    start_time = TimeField("starting time", [rq()])
    end_date = DateField("ending date", [rq()])
    end_time = TimeField("ending time", [rq()])
    submit = SubmitField("update booking")

    class Meta:
        csrf = False
