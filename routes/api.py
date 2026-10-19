from flask import Blueprint, Response, jsonify, request

from services.tags import create_tag
from services.tasks import (
    create_task,
    create_tasks,
    get_task,
    list_tasks,
    update_task_priority,
)
from services.users import (
    get_notification_pref,
    get_user,
    set_notification_pref,
)
from utils.errors import AppError, BadRequestError, ValidationError

api = Blueprint("api", __name__)

@api.errorhandler(AppError)
def handle_app_error(e):
    return jsonify({"error": e.message}), e.status_code

@api.route("/tasks", methods=["GET"])
def list_tasks_route() -> Response:
    """List all tasks, optionally filtered by the priority query parameter.

    Returns:
        A JSON list of task records.

    Raises:
        BadRequestError: If priority is not a whole number.
        ValidationError: If priority is a whole number outside 1 to 5.
    """
    raw_priority = request.args.get("priority")
    priority = None
    if raw_priority is not None:
        try:
            priority = int(raw_priority)
        except ValueError:
            raise BadRequestError(
                "priority", "must be a whole number") from None
    return jsonify(list_tasks(priority=priority))

@api.route("/tasks/<int:task_id>", methods=["GET"])
def get_task_route(task_id):
    return jsonify(get_task(task_id))

@api.route("/tasks", methods=["POST"])
def create_task_route() -> tuple[Response, int]:
    """Create a task from the JSON request body.

    Returns:
        The new task record as JSON, with status 201.

    Raises:
        ValidationError: If title or user_id is missing, or a field is
            invalid.
        NotFoundError: If no user exists with the given ID.
    """
    data = request.get_json(silent=True) or {}
    for field in ("title", "user_id"):
        if field not in data:
            raise ValidationError(field, "is required")
    # Only pass priority when the key is present, so the default (3) comes
    # from create_task alone and an explicit null is still validated.
    if "priority" in data:
        task = create_task(data["title"], data["user_id"],
                           priority=data["priority"])
    else:
        task = create_task(data["title"], data["user_id"])
    return jsonify(task), 201

@api.route("/tasks/bulk", methods=["POST"])
def create_tasks_bulk_route() -> tuple[Response, int]:
    """Create several tasks from a JSON list. Either all or none are created.

    Returns:
        The new task records as a JSON list, with status 201.

    Raises:
        ValidationError: If the body is not a non-empty list, or any item
            is invalid.
        NotFoundError: If any item's user_id doesn't match a user.
    """
    data = request.get_json(silent=True)
    if not isinstance(data, list) or not data:
        raise ValidationError("body", "must be a non-empty list of tasks")
    return jsonify(create_tasks(data)), 201

@api.route("/tasks/<int:task_id>", methods=["PATCH"])
def update_task_route(task_id: int) -> Response:
    """Update a task's priority from the JSON request body.

    Args:
        task_id: The unique identifier for the task.

    Returns:
        The updated task record as JSON.

    Raises:
        ValidationError: If priority is missing or invalid.
        NotFoundError: If no task exists with the given ID.
    """
    data = request.get_json(silent=True) or {}
    if "priority" not in data:
        raise ValidationError("priority", "is required")
    return jsonify(update_task_priority(task_id, data["priority"]))

@api.route("/tags", methods=["POST"])
def create_tag_route() -> tuple[Response, int]:
    """Create a tag from the JSON request body.

    Returns:
        The new tag record as JSON, with status 201.

    Raises:
        ValidationError: If the body is not a JSON object, or a field is
            missing or invalid.
    """
    return jsonify(create_tag(request.get_json(silent=True))), 201

@api.route("/users/<int:user_id>", methods=["GET"])
def get_user_route(user_id: int) -> Response:
    """Get a user, including their notification preference.

    Args:
        user_id: The unique identifier for the user.

    Returns:
        The user record as JSON. A notification_pref that was never set
        is shown as "none".

    Raises:
        NotFoundError: If no user exists with the given ID.
    """
    # Copy so the stored record keeps its original value.
    user = dict(get_user(user_id))
    user["notification_pref"] = get_notification_pref(user_id)
    return jsonify(user)

@api.route("/users/<int:user_id>/notifications", methods=["GET"])
def get_notifications_route(user_id: int) -> Response:
    """Get a user's notification preference.

    Args:
        user_id: The unique identifier for the user.

    Returns:
        JSON with user_id and notification_pref.

    Raises:
        NotFoundError: If no user exists with the given ID.
    """
    return jsonify({"user_id": user_id,
                    "notification_pref": get_notification_pref(user_id)})

@api.route("/users/<int:user_id>/notifications", methods=["PATCH"])
def update_notifications_route(user_id: int) -> Response:
    """Update a user's notification preference from the JSON request body.

    Args:
        user_id: The unique identifier for the user.

    Returns:
        JSON with user_id and the updated notification_pref.

    Raises:
        ValidationError: If notification_pref is missing or invalid.
        NotFoundError: If no user exists with the given ID.
    """
    data = request.get_json(silent=True) or {}
    if "notification_pref" not in data:
        raise ValidationError("notification_pref", "is required")
    user = set_notification_pref(user_id, data["notification_pref"])
    return jsonify({"user_id": user_id,
                    "notification_pref": user["notification_pref"]})
