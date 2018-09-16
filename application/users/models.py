from application import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(144), nullable=False)
    full_name = db.Column(db.String(144), nullable=False)
    pw_hash = db.Column(db.String(512), nullable=False)

    def __init__(self, username, full_name, pw_hash):
        self.username = username
        self.full_name = full_name
        self.pw_hash = pw_hash
