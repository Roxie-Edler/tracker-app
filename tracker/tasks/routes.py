import math

from flask import request, jsonify, g

from tracker.extensions import db # type: ignore
from tracker.models import User, Task # type: ignore
from tracker.auth.decorators import token_required # type: ignore
from . import tasks

@tasks.route("/tasks", methods=["POST"]) # type: ignore
@token_required
def create_task():
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

    if not set(data.keys()).issubset({"title", "description"}):
        return jsonify({
            "code": "validation_error",
            "message": "Only title and description are allowed."
        }), 400

    title = data.get("title")

    if not isinstance(title, str) or not title.strip():
        return jsonify({
            "code": "validation_error",
            "message": "A task title is required."
        }), 400

    title = title.strip()

    if len(title) > 255:
        return jsonify({
            "code": "validation_error",
            "message": "Title must be at most 255 characters."
        }), 400

    description = data.get("description")

    if description is not None and not isinstance(description, str):
        return jsonify({
            "code": "validation_error",
            "message": "Description must be a string or null."
        }), 400

    task = Task(
        user_id=g.user_id,
        title=title,
        description=description
    )

    try:
        db.session.add(task)
        db.session.commit()

    except Exception:
        db.session.rollback()
        raise

    return jsonify({
        "id": task.id,
        "user_id": task.user_id,
        "title": task.title,
        "description": task.description,
        "completed": task.completed,
        "created_at": task.created_at.isoformat()
    }), 201



@tasks.route("/tasks", methods=["GET"]) # type: ignore
@token_required
def get_tasks():
    page_param = request.args.get("page", "1")
    per_page_param = request.args.get("per_page", "20")

    try:
        page = int(page_param)
    except (TypeError, ValueError):
        return jsonify({
            "code": "validation_error",
            "message": "page must be a positive integer."
        }), 400

    try:
        per_page = int(per_page_param)
    except (TypeError, ValueError):
        return jsonify({
            "code": "validation_error",
            "message": "per_page must be a positive integer."
        }), 400

    if page < 1:
        return jsonify({
            "code": "validation_error",
            "message": "page must be a positive integer."
        }), 400

    if per_page < 1 or per_page > 100:
        return jsonify({
            "code": "validation_error",
            "message": "per_page must be between 1 and 100."
        }), 400

    total = db.session.execute(
        db.select(db.func.count(Task.id)).where(
            Task.user_id == g.user_id
        )
    ).scalar_one()

    pages = math.ceil(total / per_page)

    tasks = db.session.execute(
        db.select(Task)
        .where(Task.user_id == g.user_id)
        .order_by(Task.id.asc())
        .limit(per_page)
        .offset((page - 1) * per_page)
    ).scalars().all()

    return jsonify({
        "items": [
            {
                "id": task.id,
                "user_id": task.user_id,
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "created_at": task.created_at.isoformat()
            }
            for task in tasks
        ],
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": pages
        }
    }), 200


@tasks.route("/tasks/<int:task_id>", methods=["GET"]) # type: ignore
@token_required
def get_task(task_id):
    task = db.session.get(Task, task_id)

    if task is None:
        return jsonify({
            "code": "not_found",
            "message": "Task not found."
        }), 404
    
    if task.user_id != g.user_id:
        return jsonify({
            "code": "forbidden",
            "message": "You do not have permission to access this task."
        }), 403
    
    return jsonify({
        "id": task.id,
        "user_id": task.user_id,
        "title": task.title,
        "description": task.description,
        "completed": task.completed,
        "created_at": task.created_at.isoformat()
    }), 200

@tasks.route("/tasks/<int:task_id>", methods=["PATCH"]) # type: ignore
@token_required
def update_task(task_id):
    task = db.session.get(Task, task_id)

    if task is None:
        return jsonify({
            "code": "not_found",
            "message": "Task not found."
        }), 404

    if task.user_id != g.user_id:
        return jsonify({
            "code": "forbidden",
            "message": "You do not have permission to update this task."
        }), 403

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

    allowed_fields = {"title", "description", "completed"}

    if not data or not set(data.keys()).issubset(allowed_fields):
        return jsonify({
            "code": "validation_error",
            "message": "Provide at least one valid task field."
        }), 400

    if "title" in data:
        title = data["title"]

        if not isinstance(title, str) or not title.strip():
            return jsonify({
                "code": "validation_error",
                "message": "Title must be a non-empty string."
            }), 400

        if len(title.strip()) > 255:
            return jsonify({
                "code": "validation_error",
                "message": "Title must be at most 255 characters."
            }), 400

        task.title = title.strip()

    if "description" in data:
        description = data["description"]

        if description is not None and not isinstance(description, str):
            return jsonify({
                "code": "validation_error",
                "message": "Description must be a string or null."
            }), 400

        task.description = description

    if "completed" in data:
        completed = data["completed"]

        if not isinstance(completed, bool):
            return jsonify({
                "code": "validation_error",
                "message": "Completed must be a Boolean."
            }), 400

        task.completed = completed

    db.session.commit()

    return jsonify({
        "id": task.id,
        "user_id": task.user_id,
        "title": task.title,
        "description": task.description,
        "completed": task.completed,
        "created_at": task.created_at.isoformat()
    }), 200

@tasks.route("/tasks/<int:task_id>", methods=["DELETE"]) # type: ignore
@token_required
def delete_task(task_id):
    task = db.session.get(Task, task_id)

    if task is None:
        return jsonify({
            "code": "not_found",
            "message": "Task not found."
        }), 404

    if task.user_id != g.user_id:
        return jsonify({
            "code": "forbidden",
            "message": "You do not have permission to delete this task."
        }), 403

    db.session.delete(task)
    db.session.commit()

    return jsonify({
        "message": "Task deleted successfully.",
        "id": task_id
    }), 200