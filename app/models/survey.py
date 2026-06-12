from datetime import datetime

from app.extensions.db import db


class Survey(db.Model):
    __tablename__ = "surveys"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    title = db.Column(
        db.String(255),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
    )

    archived_at = db.Column(
        db.DateTime,
        nullable=True
    )

    is_published = db.Column(
        db.Boolean,
        default=False
    )

    researcher_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    questions = db.relationship(
        "Question",
        backref="survey",
        lazy=True,
        cascade="all, delete"
    )

