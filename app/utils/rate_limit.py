from datetime import datetime, timedelta

from app.models.answer import Answer


def can_submit_response(user_id):

    one_hour_ago = (
        datetime.utcnow() - timedelta(hours=1)
    )

    count = Answer.query.filter(
        Answer.user_id == user_id,
        Answer.created >= one_hour_ago
    ).count()

    return count < 5