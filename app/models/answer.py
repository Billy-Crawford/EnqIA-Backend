from datetime import datetime

from app.extensions.db import db


class Answer(db.Model):

    __tablename__ = "answers"


    id = db.Column(
        db.Integer,
        primary_key=True
    )


    question_id = db.Column(
        db.Integer,
        db.ForeignKey("questions.id"),
        nullable=False
    )


    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )


    value = db.Column(
        db.Text,
        nullable=True
    )


    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    options = db.relationship(
        "AnswerOption",
        backref="answer",
        lazy=True,
        cascade="all, delete"
    )

