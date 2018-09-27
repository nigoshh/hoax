from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, validators

ln = validators.Length
rq = validators.InputRequired


class CommunityFormCreate(FlaskForm):
    address = StringField("address", [rq(), ln(max=144)])
    submit = SubmitField("create community")

    class Meta:
        csrf = False


class CommunityFormUpdate(FlaskForm):
    address = StringField("address", [rq(), ln(max=144)])
    submit = SubmitField("update community")

    class Meta:
        csrf = False
