from application import db


class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    community_id = db.Column(db.Integer,
                             db.ForeignKey("community.id"), nullable=False)
    username = db.Column(db.String(144), nullable=False, unique=True)
    pw_hash = db.Column(db.String(512), nullable=False)
    apartment = db.Column(db.String(144), nullable=False)
    forename = db.Column(db.String(144), nullable=False)
    surname = db.Column(db.String(144), nullable=False)
    email = db.Column(db.String(144))
    phone = db.Column(db.String(144))

    def __init__(self, community_id, username, pw_hash,
                 apartment, forename, surname):
        self.community_id = community_id
        self.username = username
        self.pw_hash = pw_hash
        self.apartment = apartment
        self.forename = forename
        self.surname = surname

    def get_id(self):
        return self.id

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True
