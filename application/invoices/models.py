from decimal import Decimal
from flask_login import current_user
from sqlalchemy.sql import text
from application import db
from application.models import Base
from application.utils.utils import PRICE

invoice_booking = db.Table("invoice_booking",
                           db.Column("invoice_id", db.Integer,
                                     db.ForeignKey("invoice.id"),
                                     primary_key=True, index=True),
                           db.Column("booking_id", db.Integer,
                                     db.ForeignKey("booking.id"), unique=True,
                                     primary_key=True, index=True))


class Invoice(Base):
    price = db.Column(db.Numeric, db.CheckConstraint("price >= 0"),
                      nullable=False)
    paid = db.Column(db.Boolean, nullable=False, index=True)
    bookings = db.relationship("Booking", secondary=invoice_booking,
                               lazy="subquery", single_parent=True,
                               backref=db.backref("invoice", lazy=True,
                                                  cascade="all"))

    def __init__(self, bookings):
        self.paid = False
        self.bookings = bookings
        self.calculate_price()

    def __str__(self):
        return str(self.id)

    def price_str(self):
        return PRICE % self.price

    def calculate_price(self):
        self.price = sum([Decimal(b.price) for b in self.bookings])

    @staticmethod
    def get_allowed(filter_unpaid=False):
        if not current_user.is_authenticated:
            return []
        query = ("SELECT * FROM invoice WHERE id IN "
                 "(SELECT invoice_id FROM invoice_booking "
                 "INNER JOIN booking "
                 "ON invoice_booking.booking_id = booking.id "
                 "WHERE booking.account_id IN "
                 "(SELECT id FROM account "
                 "WHERE community_id IN "
                 "(SELECT community.id FROM community "
                 "INNER JOIN admin "
                 "ON community.id = admin.community_id "
                 "WHERE admin.account_id = :user_id) "
                 "OR id = :user_id)) ")
        if filter_unpaid:
            query += "AND paid = 0 "
        query += "ORDER BY date_created"
        stmt = text(query).params(user_id=current_user.get_id())
        return db.session.query(Invoice).from_statement(stmt).all()
