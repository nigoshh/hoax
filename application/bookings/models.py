from sqlalchemy import CheckConstraint, not_, or_
from application import db
from application.models import Base


class Booking(Base):
    account_id = db.Column(db.Integer,
                           db.ForeignKey("account.id"), nullable=False)
    resource_id = db.Column(db.Integer,
                            db.ForeignKey("resource.id"), nullable=False)
    start = db.Column(db.DateTime, nullable=False)
    end = db.Column(db.DateTime, nullable=False)
    __table_args__ = (CheckConstraint("start < end", name="time_direction"), )

    def __init__(self, account_id, resource_id, start, end):
        self.account_id = account_id
        self.resource_id = resource_id
        self.start = start
        self.end = end

    @staticmethod
    def is_free_time_slot(b):
        res = (db.session.query(Booking)
               .filter(Booking.resource_id == b.resource_id,
                       Booking.id != b.id,
                       not_(or_(Booking.end <= b.start,
                                Booking.start >= b.end)))
               .first())
        return res is None
