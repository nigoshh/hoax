from flask_wtf import FlaskForm
from wtforms import BooleanField, SubmitField, validators
from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField
from application.bookings.models import Booking

rq = validators.InputRequired


class InvoiceFormCreate(FlaskForm):
    bookings = QuerySelectMultipleField("bookings", [rq()],
                                        query_factory=Booking
                                        .get_allowed_by_account)
    submit = SubmitField("create invoice")

    class Meta:
        csrf = False


class InvoiceFormFilter(FlaskForm):
    filter_unpaid = BooleanField("show only unpaid invoices")

    class Meta:
        csrf = False


class InvoiceFormUpdate(FlaskForm):
    bookings = QuerySelectMultipleField("bookings", [rq()])
    paid = BooleanField("paid")
    submit = SubmitField("update invoice")

    class Meta:
        csrf = False
