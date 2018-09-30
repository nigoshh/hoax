from flask_login import current_user
from sqlalchemy.sql import text
from application import db
from application.models import Base
from sqlalchemy import UniqueConstraint


class Resource(Base):
    address = db.Column(db.String(144), nullable=False)
    type = db.Column(db.String(144), nullable=False)
    number = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    bookings = db.relationship('Booking', lazy=True,
                               backref=db.backref('resource', lazy=False),
                               cascade="all, delete-orphan")
    __table_args__ = (UniqueConstraint("address", "type", "number",
                      name="unique_atn"), )

    def __init__(self, address, type, number, price, communities):
        self.address = address
        self.type = type
        self.number = number
        self.price = price
        self.communities = communities

    @staticmethod
    def get_allowed_resources():
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
