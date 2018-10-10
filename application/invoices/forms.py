from flask_wtf import FlaskForm
from wtforms import BooleanField, DateTimeField, SubmitField, validators
from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField
from application.bookings.models import Booking

rq = validators.InputRequired


class InvoiceFormCreate(FlaskForm):
    bookings = QuerySelectMultipleField("bookings", [rq()],
                                        query_factory=Booking.get_allowed)
    submit = SubmitField("create invoice")

    class Meta:
        csrf = False


class InvoiceFormUpdate(FlaskForm):
    bookings = QuerySelectMultipleField("bookings", [rq()],
                                        query_factory=Booking.get_allowed)
    sent = DateTimeField("sent")
    due = DateTimeField("due")
    payed = BooleanField("payed")
    submit = SubmitField("update invoice")

    class Meta:
        csrf = False
