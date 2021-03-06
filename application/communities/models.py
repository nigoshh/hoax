from flask_login import current_user
from sqlalchemy.sql import text
from application import db
from application.models import Base

community_resource = db.Table("community_resource",
                              db.Column("community_id", db.Integer,
                                        db.ForeignKey("community.id"),
                                        primary_key=True, index=True),
                              db.Column("resource_id", db.Integer,
                                        db.ForeignKey("resource.id"),
                                        primary_key=True, index=True))


class Community(Base):
    address = db.Column(db.String(144), nullable=False, unique=True)
    accounts = db.relationship("Account", lazy=True,
                               backref=db.backref("community", lazy=False),
                               cascade="all, delete-orphan")
    resources = db.relationship("Resource", secondary=community_resource,
                                lazy="subquery",
                                backref=db.backref("communities", lazy=True))

    def __init__(self, address):
        self.address = address

    def __str__(self):
        return self.address

    @staticmethod
    def get_all():
        return Community.query.order_by("address")

    @staticmethod
    def get_allowed():
        if not current_user.is_authenticated:
            return []
        stmt = text("SELECT * FROM community "
                    "WHERE id IN "
                    "(SELECT community.id FROM community "
                    "INNER JOIN admin ON community.id = admin.community_id "
                    "WHERE admin.account_id = :user_id) "
                    "ORDER BY address").params(user_id=current_user.get_id())
        return db.session.query(Community).from_statement(stmt).all()

    @staticmethod
    def list_with_stats():
        stmt = text("SELECT community.id, community.address, "
                    "COUNT(DISTINCT account.id) "
                    "AS accounts, "
                    "COUNT(DISTINCT community_resource.resource_id) "
                    "AS resources "
                    "FROM community "
                    "LEFT JOIN account "
                    "ON account.community_id = community.id "
                    "LEFT JOIN community_resource "
                    "ON community_resource.community_id = community.id "
                    "GROUP BY community.id "
                    "ORDER BY resources DESC, accounts DESC, "
                    "community.address")
        res = db.engine.execute(stmt)

        list = []
        for row in res:
            list.append({"id": row[0], "address": row[1],
                         "accounts": row[2], "resources": row[3]})

        return list
