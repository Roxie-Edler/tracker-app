from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException

from .extensions import db, migrate
from .main import main as main_bp # type: ignore
from .auth import auth as auth_bp # type: ignore
from config import config_by_name # type: ignore # type: ignore
from . import models
from .tasks import tasks as tasks_bp # type: ignore


def create_app(config_name):
    app = Flask(__name__)

    app.config.from_object(config_by_name[config_name])

    print("DATABASE URI:", app.config["SQLALCHEMY_DATABASE_URI"])

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(tasks_bp, url_prefix="/auth")

    error_messages = {
        400: ("bad_request", "Bad request."),
        401: ("authentication_error", "Authentication required."),
        403: ("forbidden", "Access forbidden."),
        404: ("not_found", "Resource not found."),
        405: ("method_not_allowed", "Method not allowed."),
        500: ("internal_server_error", "Internal server error.")
    }

    for status_code, (error_code, message) in error_messages.items():
        def make_handler(code, description):
            def handler(error):
                return jsonify({
                    "code": code,
                    "message": description
                }), code
            return handler
        
        app.register_error_handler(
            status_code,
            make_handler(error_code, message)
        )

    return app