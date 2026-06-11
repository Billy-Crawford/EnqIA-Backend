from app.extensions.db import db


class AnswerOption(db.Model):

    __tablename__ = "answer_options"


    id = db.Column(
        db.Integer,
        primary_key=True
    )


    answer_id = db.Column(
        db.Integer,
        db.ForeignKey("answers.id"),
        nullable=False
    )


    option_value = db.Column(
        db.String(255),
        nullable=False
    )

