from functools import wraps

import jwt
from flask import current_app, request, jsonify, g


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return jsonify({
                "code": "authentication_error",
                "message": "Authorization token is required."
            }), 401

        parts = auth_header.split()

        if len(parts) != 2 or parts[0].lower() != "bearer":
            return jsonify({
                "code": "authentication_error",
                "message": "Authorization header must use Bearer token format."
            }), 401

        token = parts[1]

        try:
            payload = jwt.decode(
                token,
                current_app.config["JWT_SECRET"],
                algorithms=["HS256"],
                options={"require": ["exp", "sub"]}
            )

            user_id = int(payload["sub"])

        except (jwt.InvalidTokenError, TypeError, ValueError, KeyError):
            return jsonify({
                "code": "authentication_error",
                "message": "Invalid or expired token."
            }), 401

        g.user_id = user_id

        return f(*args, **kwargs)

    return decorated