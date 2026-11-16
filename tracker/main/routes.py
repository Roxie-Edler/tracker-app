from . import main
from flask import request, jsonify
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError

from tracker.extensions import db # type: ignore
from tracker.models import User # type: ignore


@main.route("/")
def index():
    return "Hello from the main blueprint!"

@main.route("/health", methods=["GET"])
def health():
    return {"status": "healthy"}, 200

@main.route("/register", methods=["POST"])
def register():
    if not request.is_json:
        return jsonify({
            "code": "validation_error",
            "message": "Request must contain JSON."
        }), 400

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "code": "validation_error",
            "message": "Request body must be a JSON object."
        }), 400

    email = data.get("email")
    password = data.get("password")

    if not isinstance(email, str) or not isinstance(password, str):
        return jsonify({
            "code": "validation_error",
            "message": "Email and password must be strings."
        }), 400

    if not email or not password:
        return jsonify({
            "code": "validation_error",
            "message": "Email and password are required."
        }), 400

    if len(email) > 255 or len(password) > 128:
        return jsonify({
            "code": "validation_error",
            "message": "Email must be at most 255 characters and password at most 128 characters."
        }), 400

    existing_user = db.session.execute(
        db.select(User).where(User.email == email)
    ).scalar_one_or_none()

    if existing_user:
        return jsonify({
            "code": "duplicate_email",
            "message": "An account with this email already exists."
        }), 409

    user = User(
        email=email,
        password_hash=generate_password_hash(password)
    )

    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            "code": "duplicate_email",
            "message": "An account with this email already exists."
        }), 409

    return jsonify({
        "id": user.id,
        "email": user.email,
        "created_at": user.created_at.isoformat()
    }), 201