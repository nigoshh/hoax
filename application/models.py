from datetime import datetime as dt
from application import db


class Base(db.Model):

    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=dt.utcnow, nullable=False)
    date_modified = db.Column(db.DateTime, default=dt.utcnow, onupdate=dt.utcnow,
                              nullable=False)
