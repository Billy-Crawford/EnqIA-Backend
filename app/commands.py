from werkzeug.security import generate_password_hash

from app.extensions.db import db
from app.models.user import User


def register_commands(app):

    @app.cli.command("create-admin")
    def create_admin():

        email = "admin@enqia.com"

        existing_admin = User.query.filter_by(
            email=email
        ).first()

        if existing_admin:
            print("Admin already exists")
            return

        admin = User(
            firstname="System",
            lastname="Administrator",
            email=email,
            password=generate_password_hash("CTBF-EnqIA"),
            role="admin"
        )

        db.session.add(admin)
        db.session.commit()

        print("Admin created successfully")