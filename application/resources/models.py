from decimal import Decimal, ROUND_DOWN
from flask_login import current_user
from sqlalchemy.sql import text
from application import db
from application.models import Base
from sqlalchemy import UniqueConstraint


class Resource(Base):
    account_id = db.Column(db.Integer, db.ForeignKey("account.id"),
                           nullable=False, index=True)
    address = db.Column(db.String(144), nullable=False)
    type = db.Column(db.String(144), nullable=False, index=True)
    name = db.Column(db.String(144), nullable=False)
    price = db.Column(db.Numeric,
                      db.CheckConstraint("price >= 0 AND price <= 1000000"),
                      nullable=False)
    bookings = db.relationship("Booking", lazy=True,
                               backref=db.backref("resource", lazy=False),
                               cascade="all, delete-orphan")
    __table_args__ = (UniqueConstraint("address", "type", "name",
                      name="unique_atn"), )

    def __init__(self, account_id, address, type, name, price, communities):
        self.account_id = account_id
        self.address = address
        self.type = type
        self.name = name
        self.price = price
        self.communities = communities

    def __str__(self):
        return "%s, %s %s" % (self.address, self.type, self.name)

    def price_rnd(self):
        return self.price.quantize(Decimal('.01'), rounding=ROUND_DOWN)

    def price_str(self):
        return "%.2f €" % self.price

    @staticmethod
    def get_all():
        stmt = text("SELECT * FROM resource "
                    "ORDER BY address, type, name")
        return db.session.query(Resource).from_statement(stmt).all()

    @staticmethod
    def get_allowed():
        if not current_user.is_authenticated:
            return []
        stmt = text("SELECT * FROM resource WHERE id IN "
                    "(SELECT DISTINCT resource_id "
                    "FROM community_resource, admin "
                    "WHERE community_resource.community_id "
                    "= admin.community_id "
                    "AND admin.account_id = 1) "
                    "OR id IN "
                    "(SELECT DISTINCT resource_id "
                    "FROM community_resource, account "
                    "WHERE community_resource.community_id "
                    "= account.community_id "
                    "AND account.id = 1)"
                    ).params(user_id=current_user.get_id())
        return db.session.query(Resource).from_statement(stmt).all()
