from app.extensions.db import db

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    firstname= db.Column(
        db.String(100),
        nullable=False
    )

    lastname = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )

    role = db.Column(
        db.String(50),
        nullable=False
    )

    surveys = db.relationship(
        "Survey",
        backref="researcher",
        lazy=True
    )



