from datetime import datetime as dt
from decimal import Decimal, ROUND_DOWN
from flask_login import current_user
from sqlalchemy import CheckConstraint, text
from application import db
from application.models import Base
from application.resources.models import Resource
from application.utils.utils import PRICE


# to avoid strange type errors with str / datetime
def check_type_dt(datetime):
    if type(datetime) is str:
        return dt.fromisoformat(datetime)
    return datetime


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
        start_dt = check_type_dt(self.start_dt)
        start_date = start_dt.strftime("%Y-%m-%d")
        return (PRICE + ", %s, %s, %s") % (self.price, self.account,
                                           self.resource, start_date)

    def str_no_account(self):
        start_dt = check_type_dt(self.start_dt).strftime("%Y-%m-%d %H:%M")
        return (PRICE + ", %s, %s") % (self.price, self.resource, start_dt)

    def start_date_str(self):
        return check_type_dt(self.start_dt).strftime("%Y-%m-%d")

    def start_time_str(self):
        return check_type_dt(self.start_dt).strftime("%H:%M")

    def end_date_str(self):
        return check_type_dt(self.end_dt).strftime("%Y-%m-%d")

    def end_time_str(self):
        return check_type_dt(self.end_dt).strftime("%H:%M")

    def price_str(self):
        return PRICE % self.price

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
        stmt = (text(query + " AND id <> :booking_id"
                     ).params(booking_id=b.id, resource_id=b.resource_id,
                              start_dt=b.start_dt, end_dt=b.end_dt)
                if b.id else
                text(query
                     ).params(resource_id=b.resource_id,
                              start_dt=b.start_dt, end_dt=b.end_dt))
        return not db.engine.execute(stmt).fetchone()

    @staticmethod
    def get_allowed_by_account(invoice_id=None):
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
        query += ") ORDER BY start_dt"
        stmt = text(query).params(params)
        return db.session.query(Booking).from_statement(stmt).all()

    @staticmethod
    def get_allowed_by_resource(from_dt=None, to_dt=None, resource_ids=None,
                                filter_not_in_invoice=False):
        if not current_user.is_authenticated:
            return []
        query = ("SELECT * FROM booking WHERE (resource_id IN "
                 "(SELECT DISTINCT community_resource.resource_id "
                 "FROM community_resource INNER JOIN admin "
                 "ON admin.community_id = community_resource.community_id "
                 "WHERE admin.account_id = :user_id) "
                 "OR resource_id IN "
                 "(SELECT community_resource.resource_id "
                 "FROM community_resource INNER JOIN account "
                 "ON account.community_id = community_resource.community_id "
                 "WHERE account.id = :user_id))")
        params = {"user_id": current_user.get_id()}
        if from_dt:
            query += " AND end_dt > :from_dt"
            params["from_dt"] = from_dt
        if to_dt:
            query += " AND start_dt < :to_dt"
            params["to_dt"] = to_dt
        if resource_ids:
            query += " AND resource_id IN (:resource_id_0"
            params["resource_id_0"] = resource_ids[0]
            list_length = len(resource_ids)
            if list_length > 1:
                for i in range(1, list_length):
                    query += ", :resource_id_%d" % i
                    params["resource_id_%d" % i] = resource_ids[i]
            query += ")"
        if filter_not_in_invoice:
            query += (" AND id NOT IN "
                      "(SELECT DISTINCT booking_id FROM invoice_booking)")
        query += " ORDER BY start_dt"
        stmt = text(query).params(params)
        return db.session.query(Booking).from_statement(stmt).all()
