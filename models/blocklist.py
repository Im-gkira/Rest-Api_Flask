from db import db


class BlockedJwt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    access_token = db.Column(db.String, nullable=False, unique=True)


