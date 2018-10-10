from application import db
from application.models import Base

invoice_booking = db.Table("invoice_booking",
                           db.Column("invoice_id", db.Integer,
                                     db.ForeignKey("invoice.id"),
                                     primary_key=True),
                           db.Column("booking_id", db.Integer,
                                     db.ForeignKey("booking.id"),
                                     primary_key=True, unique=True))


class Invoice(Base):
    price = db.Column(db.Numeric, db.CheckConstraint("price >= 0"),
                      nullable=False)
    sent = db.Column(db.DateTime)
    due = db.Column(db.DateTime)
    paid = db.Column(db.Boolean, nullable=False)
    bookings = db.relationship("Booking", secondary=invoice_booking,
                               lazy="subquery", single_parent=True,
                               backref=db.backref("invoice", lazy=True,
                                                  cascade="all"))

    def __init__(self):
        self.paid = False

    def __str__(self):
        return str(self.id) + str(self.date_modified)

    def price_str(self):
        return "%.2f €" % self.price
