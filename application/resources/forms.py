from decimal import ROUND_DOWN
from flask_wtf import FlaskForm
from wtforms import DecimalField, StringField, SubmitField, validators
from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField
from application.communities.models import Community

rq = validators.InputRequired
ln = validators.Length
nr = validators.NumberRange
opt = validators.Optional
nr_msg = "Price must be between %(min)s and %(max)s (both inclusive)."


def all_c():
    return Community.query.all()


class ResourceFormCreate(FlaskForm):
    address = StringField("address", [rq(), ln(max=144)])
    type = StringField("type", [rq(), ln(max=144)])
    name = StringField("name/identifier", [rq(), ln(max=144)])
    price = DecimalField("price (€/hour)", [rq(), nr(min=0, max=1000000,
                         message=nr_msg)], rounding=ROUND_DOWN)
    communities = QuerySelectMultipleField("allowed communities",
                                           get_label="address",
                                           query_factory=all_c)
    submit = SubmitField("create resource")

    class Meta:
        csrf = False


class ResourceFormUpdate(FlaskForm):
    address = StringField("address", [ln(max=144)])
    type = StringField("type", [ln(max=144)])
    name = StringField("name/identifier", [ln(max=144)])
    price = DecimalField("price (€/hour)", [nr(min=0, max=1000000,
                         message=nr_msg), opt()], rounding=ROUND_DOWN)
    communities = QuerySelectMultipleField("allowed communities",
                                           get_label="address",
                                           query_factory=all_c)
    submit = SubmitField("update resource")

    class Meta:
        csrf = False
