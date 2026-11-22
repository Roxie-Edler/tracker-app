from flask import request, jsonify, g
from sqlalchemy.exc import IntegrityError

from tracker.extensions import db # type: ignore
from tracker.models import User # type: ignore
from .decorators import token_required
from . import auth

def serialize_profile(user):
    return {
        "id": user.id,
        "email": user.email,
        "created_at": user.created_at.isoformat()
    }


@auth.route("/protected-test", methods=["GET"])
@token_required
def protected_test():
    return jsonify({
        "message": "You are authenticated.",
        "user_id": g.user_id
    }), 200

@auth.route("/profile", methods=["GET"])
@token_required
def get_profile():
    user = db.session.get(User, g.user_id)

    if user is None:
        return jsonify({
            "code": "not_found",
            "message": "User not found."
        }), 404

    return jsonify(serialize_profile(user)), 200


@auth.route("/profile", methods=["PATCH"])
@token_required
def update_profile():
    user = db.session.get(User, g.user_id)

    if user is None:
        return jsonify({
            "code": "not_found",
            "message": "User not found."
        }), 404

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

    if set(data.keys()) != {"email"}:
        return jsonify({
            "code": "validation_error",
            "message": "Only email can be updated."
        }), 400

    email = data.get("email")

    if not isinstance(email, str) or not email.strip():
        return jsonify({
            "code": "validation_error",
            "message": "A valid email is required."
        }), 400

    email = email.strip()

    if len(email) > 255:
        return jsonify({
            "code": "validation_error",
            "message": "Email must be at most 255 characters."
        }), 400

    existing_user = db.session.execute(
        db.select(User).where(
            User.email == email,
            User.id != g.user_id
        )
    ).scalar_one_or_none()

    if existing_user:
        return jsonify({
            "code": "duplicate_email",
            "message": "An account with this email already exists."
        }), 409

    user.email = email

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            "code": "duplicate_email",
            "message": "An account with this email already exists."
        }), 409

    return jsonify(serialize_profile(user)), 200

@auth.route("/admin", methods=["GET"])
@token_required
def admin_only():
    user = db.session.get(User, g.user_id)

    if user is None:
        return jsonify({
            "code": "not_found",
            "message": "User not found."
        }), 404

    if user.role != "admin":
        return jsonify({
            "code": "forbidden",
            "message": "Admin access required."
        }), 403

    return jsonify({
        "message": "Welcome, admin!"
    }), 200