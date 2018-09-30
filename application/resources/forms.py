from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, SubmitField, validators
from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField
from application.communities.models import Community

ln = validators.Length
rq = validators.InputRequired
opt = validators.Optional


def all_c():
    return Community.query.all()


class ResourceFormCreate(FlaskForm):
    address = StringField("address", [rq(), ln(max=144)])
    type = StringField("type", [rq(), ln(max=144)])
    number = IntegerField("number", [rq()])
    price = IntegerField("price", [rq()])
    communities = QuerySelectMultipleField("communities", get_label="address",
                                           query_factory=all_c)
    submit = SubmitField("create resource")

    class Meta:
        csrf = False


class ResourceFormUpdate(FlaskForm):
    address = StringField("address", [ln(max=144)])
    type = StringField("type", [ln(max=144)])
    number = IntegerField("number", [opt()])
    price = IntegerField("price", [opt()])
    communities = QuerySelectMultipleField("communities", get_label="address",
                                           query_factory=all_c)
    submit = SubmitField("update resource")

    class Meta:
        csrf = False
