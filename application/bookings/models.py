from datetime import datetime as dt
from decimal import Decimal, ROUND_DOWN
from flask_login import current_user
from sqlalchemy import CheckConstraint, text
from application import db
from application.models import Base
from application.resources.models import Resource


class Booking(Base):
    account_id = db.Column(db.Integer, db.ForeignKey("account.id"),
                           nullable=False, index=True)
    resource_id = db.Column(db.Integer, db.ForeignKey("resource.id"),
                            nullable=False, index=True)
    start_dt = db.Column(db.DateTime, nullable=False, index=True)
    end_dt = db.Column(db.DateTime, nullable=False, index=True)
    price = db.Column(db.Numeric, db.CheckConstraint("price >= 0"),
                      nullable=False)
    __table_args__ = (CheckConstraint("start_dt < end_dt",
                                      name="time_direction"), )

    def __init__(self, account_id, resource_id, start_dt, end_dt):
        self.account_id = account_id
        self.resource_id = resource_id
        self.start_dt = start_dt
        self.end_dt = end_dt
        self.calculate_price()

    def __str__(self):
        start_dt = ""
        if type(self.start_dt) is str:
            start_dt = dt.fromisoformat(self.start_dt)
        else:
            start_dt = self.start_dt
        start_date = start_dt.strftime("%d/%m/%Y")
        return "%.2f €, %s, %s, %s" % (self.price, self.account,
                                       self.resource, start_date)

    def str_no_account(self):
        start_dt = self.start_dt.strftime("%d/%m/%Y %H:%M")
        return "%.2f €, %s, %s" % (self.price, self.resource, start_dt)

    def start_date_str(self):
        return self.start_dt.strftime("%d/%m/%Y")

    def start_time_str(self):
        return self.start_dt.strftime("%H:%M")

    def end_date_str(self):
        return self.end_dt.strftime("%d/%m/%Y")

    def end_time_str(self):
        return self.end_dt.strftime("%H:%M")

    def price_str(self):
        return "%.2f €" % self.price

    def calculate_price(self):
        time_span = self.end_dt - self.start_dt
        hours = Decimal(time_span.total_seconds()) / 3600
        price = Resource.query.get(self.resource_id).price * hours
        self.price = price.quantize(Decimal('.01'), rounding=ROUND_DOWN)

    @staticmethod
    def is_free_time_slot(b):
        query = ("SELECT id FROM booking "
                 "WHERE resource_id = :resource_id "
                 "AND end_dt > :start_dt "
                 "AND start_dt < :end_dt")
        stmt = (text(query + " AND id <> :id"
                     ).params(id=b.id, resource_id=b.resource_id,
                              start_dt=b.start_dt, end_dt=b.end_dt)
                if b.id else
                text(query
                     ).params(resource_id=b.resource_id,
                              start_dt=b.start_dt, end_dt=b.end_dt))
        return not db.engine.execute(stmt).fetchone()

    @staticmethod
    def get_allowed(invoice_id=None):
        if not current_user.is_authenticated:
            return []
        query = ("SELECT * FROM booking WHERE (account_id IN "
                 "(SELECT account.id FROM account "
                 "INNER JOIN admin "
                 "ON account.community_id = admin.community_id "
                 "WHERE admin.account_id = :user_id) "
                 "OR account_id = :user_id) "
                 "AND id NOT IN "
                 "(SELECT booking_id FROM invoice_booking")
        params = {"user_id": current_user.get_id()}
        if invoice_id:
            query += " WHERE invoice_id <> :invoice_id"
            params["invoice_id"] = invoice_id
        query += ")"
        stmt = text(query).params(params)
        return db.session.query(Booking).from_statement(stmt).all()
