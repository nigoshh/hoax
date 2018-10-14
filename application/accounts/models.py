from flask_login import current_user
from sqlalchemy.sql import text
from application import db
from application.models import Base

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
                    "OR id = :user_id").params(user_id=current_user.get_id())
        return db.session.query(Account).from_statement(stmt).all()

    @staticmethod
    def access_allowed(id):
        return (current_user and ((ADMIN in current_user.roles())
                                  or str(current_user.get_id()) == id))
