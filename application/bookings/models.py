from sqlalchemy import and_, or_
from application import db
from application.models import Base


class Booking(Base):
    account_id = db.Column(db.Integer,
                           db.ForeignKey("account.id"), nullable=False)
    resource_id = db.Column(db.Integer,
                            db.ForeignKey("resource.id"), nullable=False)
    start = db.Column(db.DateTime, nullable=False)
    end = db.Column(db.DateTime, nullable=False)

    def __init__(self, account_id, resource_id, start, end):
        self.account_id = account_id
        self.resource_id = resource_id
        self.start = start
        self.end = end

    @staticmethod
    def is_free_time_slot(b):
        res = (db.session.query(Booking)
               .filter(Booking.resource_id == b.resource_id,
                       or_(and_(Booking.start <= b.start,
                                Booking.end > b.start),
                           and_(Booking.start > b.start,
                                Booking.start < b.end)))
               .first())
        return res is None


# textual sql version (uses LIMIT which doens't work in some databases):
# SELECT * FROM booking WHERE resource_id = :resource_id AND ((start <= :start
# AND end > :start) OR (start > :start AND start < :end)) LIMIT 1
