from application import db
from application.models import Base

community_resource = db.Table("community_resource",
                              db.Column("community_id", db.Integer,
                                        db.ForeignKey("community.id"),
                                        primary_key=True),
                              db.Column("resource_id", db.Integer,
                                        db.ForeignKey("resource.id"),
                                        primary_key=True))


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
