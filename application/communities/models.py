from application import db


class Community(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(144), nullable=False, unique=True)
    accounts = db.relationship('Account', lazy=True,
                               backref=db.backref('community', lazy=False))

    def __init__(self, address):
        self.address = address
