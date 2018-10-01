from sqlalchemy import CheckConstraint, text
from application import db
from application.models import Base


class Booking(Base):
    account_id = db.Column(db.Integer,
                           db.ForeignKey("account.id"), nullable=False)
    resource_id = db.Column(db.Integer,
                            db.ForeignKey("resource.id"), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    __table_args__ = (CheckConstraint("start_time < end_time",
                                      name="time_direction"), )

    def __init__(self, account_id, resource_id, start_time, end_time):
        self.account_id = account_id
        self.resource_id = resource_id
        self.start_time = start_time
        self.end_time = end_time

    @staticmethod
    def is_free_time_slot(b):
        query = ("SELECT id FROM booking "
                 "WHERE resource_id = :resource_id "
                 "AND end_time > :start_time "
                 "AND start_time < :end_time")
        stmt = (text(query + " AND id <> :id"
                     ).params(id=b.id, resource_id=b.resource_id,
                              start_time=b.start_time, end_time=b.end_time)
                if b.id else
                text(query
                     ).params(resource_id=b.resource_id,
                              start_time=b.start_time, end_time=b.end_time))
        return not db.engine.execute(stmt).fetchone()
