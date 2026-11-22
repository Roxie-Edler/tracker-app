from flask import jsonify, g

from . import auth
from .decorators import token_required


@auth.route("/protected-test", methods=["GET"])
@token_required
def protected_test():
    return jsonify({
        "message": "You are authenticated.",
        "user_id": g.user_id
    }), 200