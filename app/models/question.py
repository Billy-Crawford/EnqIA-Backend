from app.extensions.db import db


class Question(db.Model):

    __tablename__ = "questions"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    survey_id = db.Column(
        db.Integer,
        db.ForeignKey("surveys.id"),
        nullable=False
    )

    title = db.Column(
        db.String(500),
        nullable=False
    )

    type = db.Column(
        db.String(50),
        nullable=False
    )

    options = db.Column(
        db.JSON,
        nullable=True
    )

    answers = db.relationship(
        "Answer",
        backref="question",
        lazy=True,
        cascade="all, delete"
    )


