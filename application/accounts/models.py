from datetime import datetime
from flask_login import current_user
from sqlalchemy.sql import text
from application import db
from application.models import Base
from application.utils.utils import PRICE

ADMIN = "ADMIN"

admin = db.Table("admin",
                 db.Column("account_id", db.Integer,
                           db.ForeignKey("account.id"),
                           primary_key=True, index=True),
                 db.Column("community_id", db.Integer,
                           db.ForeignKey("community.id"),
                           primary_key=True, index=True))


class Account(Base):
    community_id = db.Column(db.Integer, db.ForeignKey("community.id"),
                             nullable=False, index=True)
    username = db.Column(db.String(144), nullable=False,
                         unique=True, index=True)
    pw_hash = db.Column(db.String(512), nullable=False)
    apartment = db.Column(db.String(144), nullable=False)
    forename = db.Column(db.String(144), nullable=False)
    surname = db.Column(db.String(144), nullable=False)
    email = db.Column(db.String(144))
    phone = db.Column(db.String(144))
    bookings = db.relationship("Booking", lazy=True,
                               backref=db.backref("account", lazy=False),
                               cascade="all, delete-orphan")
    resources = db.relationship("Resource", lazy=True,
                                backref=db.backref("account", lazy=False),
                                cascade="all, delete-orphan")
    admin_communities = db.relationship("Community", backref=db.backref(
                                        "admins", lazy=True), lazy="subquery",
                                        secondary=admin)

    def __init__(self, community_id, username, pw_hash,
                 apartment, forename, surname, email, phone):
        self.community_id = community_id
        self.username = username
        self.pw_hash = pw_hash
        self.apartment = apartment
        self.forename = forename
        self.surname = surname
        self.email = email
        self.phone = phone

    def get_id(self):
        return self.id

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True

    def roles(self):
        return [ADMIN] if len(self.admin_communities) > 0 else ["USER"]

    def __str__(self):
        return self.username

    @staticmethod
    def get_allowed():
        if not current_user.is_authenticated:
            return []
        stmt = text("SELECT * FROM account "
                    "WHERE community_id IN "
                    "(SELECT community.id FROM community "
                    "INNER JOIN admin ON community.id = admin.community_id "
                    "WHERE admin.account_id = :user_id) "
                    "OR id = :user_id "
                    "ORDER BY username").params(user_id=current_user.get_id())
        return db.session.query(Account).from_statement(stmt).all()

    @staticmethod
    def list_with_debt():
        if not current_user.is_authenticated:
            return []
        stmt = text("SELECT account.id, account.username, "
                    "account.apartment, community.address, "
                    "COALESCE(debt.debt, 0) AS account_debt "
                    "FROM community LEFT JOIN admin "
                    "ON admin.community_id = community.id "
                    "INNER JOIN account "
                    "ON account.community_id = community.id "
                    "LEFT JOIN "
                    "(SELECT booking.account_id, SUM(booking.price) AS debt "
                    "FROM booking "
                    "LEFT JOIN invoice_booking "
                    "ON invoice_booking.booking_id = booking.id "
                    "LEFT JOIN invoice "
                    "ON invoice.id = invoice_booking.invoice_id "
                    "WHERE booking.start_dt <= :current_dt "
                    "AND invoice.paid IS NOT :true "
                    "GROUP BY booking.account_id"
                    ") AS debt "
                    "ON debt.account_id = account.id "
                    "WHERE admin.account_id = :user_id "
                    "OR account.id = :user_id "
                    "ORDER BY account_debt DESC, account.date_created DESC"
                    ).params(current_dt=datetime.now(), true=True,
                             user_id=current_user.get_id())
        res = db.engine.execute(stmt)

        list = []
        for row in res:
            list.append({"id": row[0], "username": row[1], "apartment": row[2],
                         "community": row[3], "debt": PRICE % row[4]})

        return list
