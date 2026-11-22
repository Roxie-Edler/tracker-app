from flask import Flask
from .extensions import db, migrate
from .main import main as main_bp # type: ignore
from .auth import auth as auth_bp # type: ignore
from config import config_by_name # type: ignore # type: ignore
from . import models


def create_app(config_name):
    app = Flask(__name__)

    app.config.from_object(config_by_name[config_name])

    print("DATABASE URI:", app.config["SQLALCHEMY_DATABASE_URI"])

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")

    return app