from flask import Flask

from app.commands import register_commands
from app.config.settings import Config
from app.extensions.db import db
from app.extensions.migrate import migrate
from app.extensions.jwt import jwt
from app.routes import statistics
from app.routes.answers import answers_bp
from app.routes.auth import auth_bp
from app.routes.questions import questions_bp
from app.routes.statistics import statistics_bp
from app.routes.surveys import surveys_bp
from app.routes.users import users_bp
from app.routes.dashboard import dashboard_bp
from flasgger import Swagger
from flask_cors import CORS


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)
    Swagger(app)

    CORS(
        app,
        supports_credentials=True,
        origins=[
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://192.168.1.68:3000",
        ],
        allow_headers=["Content-Type", "Authorization"],
    )

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    from app.models import User

    from app.routes.main import main_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(surveys_bp)
    app.register_blueprint(questions_bp)
    app.register_blueprint(answers_bp)
    app.register_blueprint(statistics_bp)
    app.register_blueprint(dashboard_bp)

    register_commands(app)

    return app


