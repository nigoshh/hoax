from decimal import ROUND_DOWN
from flask_wtf import FlaskForm
from wtforms import (DecimalField, SelectField, StringField, SubmitField,
                     validators)
from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField
from application.communities.models import Community

rq = validators.InputRequired
ln = validators.Length
nr = validators.NumberRange
opt = validators.Optional
nr_msg = "Price must be between %(min)s and %(max)s (both inclusive)."


class ResourceFormCreate(FlaskForm):
    address = StringField("address", [rq(), ln(max=144)])
    type = StringField("type", [rq(), ln(max=144)])
    name = StringField("name/identifier", [rq(), ln(max=144)])
    price = DecimalField("price (€/hour)", [rq(), nr(min=0, max=1000000,
                         message=nr_msg)], rounding=ROUND_DOWN)
    communities = QuerySelectMultipleField("allowed communities",
                                           query_factory=Community.get_all)
    submit = SubmitField("create resource")

    class Meta:
        csrf = False


class ResourceFormFilter(FlaskForm):
    column = SelectField(
        "filter by", default="type",
        choices=[(s, s) for s in ["address", "type", "name", "price"]])
    keyword = StringField("keyword", [ln(max=256)])

    class Meta:
        csrf = False


class ResourceFormUpdate(FlaskForm):
    address = StringField("address", [ln(max=144)])
    type = StringField("type", [ln(max=144)])
    name = StringField("name/identifier", [ln(max=144)])
    price = DecimalField("price (€/hour)", [nr(min=0, max=1000000,
                         message=nr_msg), opt()], rounding=ROUND_DOWN)
    communities = QuerySelectMultipleField("allowed communities",
                                           query_factory=Community.get_all)
    submit = SubmitField("update resource")

    class Meta:
        csrf = False
