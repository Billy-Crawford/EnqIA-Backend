from app.extensions.db import db
from app.models.event_log import EventLog

def log_event(user_id, action):

    event = EventLog(
        user_id=user_id,
        action=action
    )

    db.session.add(event)
    db.session.commit()

