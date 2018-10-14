from flask_wtf import FlaskForm
from wtforms import SubmitField, validators
from wtforms.fields.html5 import DateField, TimeField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
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
