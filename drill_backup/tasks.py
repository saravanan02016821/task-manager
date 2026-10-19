from services.users import USERS
from utils.errors import AppError, NotFoundError, ValidationError

DEFAULT_PRIORITY = 3

TASKS: dict[int, dict] = {
    1: {"id": 1, "title": "Buy groceries",  "done": False, "user_id": 1,
        "priority": 3},
    2: {"id": 2, "title": "Write report",   "done": False, "user_id": 1,
        "priority": 3},
    3: {"id": 3, "title": "Call dentist",   "done": True,  "user_id": 2,
        "priority": 3},
}

def _validate_priority(priority: int) -> None:
    """Check that a priority value is an integer from 1 to 5.

    Args:
        priority: The priority value to check.

    Raises:
        ValidationError: If priority is not an integer between 1 and 5.
    """
    if (not isinstance(priority, int) or isinstance(priority, bool)
            or not 1 <= priority <= 5):
        raise ValidationError("priority", "must be an integer between 1 and 5")

def process_order(task_id: int) -> dict:
    """Mark a task as done.

    Args:
        task_id: The unique identifier for the task.

    Returns:
        The updated task record.

    Raises:
        NotFoundError: If no task exists with the given ID.
    """
    if task_id not in TASKS:
        raise NotFoundError("Task")
    task = TASKS[task_id]
    task["done"] = True
    return task

def get_task(task_id: int) -> dict:
    """Retrieve a task by ID.

    Args:
        task_id: The unique identifier for the task.

    Returns:
        The task record as a dictionary.

    Raises:
        NotFoundError: If no task exists with the given ID.
    """
    if task_id not in TASKS:
        raise NotFoundError("Task")
    return TASKS[task_id]

def _validate_new_task(title: str, user_id: int, priority: int) -> None:
    """Check that the fields for a new task are valid.

    Args:
        title: The task's title.
        user_id: The ID of the user who owns the task.
        priority: The task's priority.

    Raises:
        ValidationError: If title is empty or priority is not an integer
            between 1 and 5.
        NotFoundError: If no user exists with the given ID.
    """
    if not title or not title.strip():
        raise ValidationError("title", "cannot be empty")
    _validate_priority(priority)
    if user_id not in USERS:
        raise NotFoundError("User")

def create_task(title: str, user_id: int,
                priority: int = DEFAULT_PRIORITY) -> dict:
    """Create a new task.

    Args:
        title: The task's title.
        user_id: The ID of the user who owns the task.
        priority: The task's priority, from 1 to 5. Defaults to 3.

    Returns:
        The newly created task record.

    Raises:
        ValidationError: If title is empty or priority is not an integer
            between 1 and 5.
        NotFoundError: If no user exists with the given ID.
    """
    _validate_new_task(title, user_id, priority)
    new_id = max(TASKS.keys()) + 1
    TASKS[new_id] = {"id": new_id, "title": title,
                     "done": False, "user_id": user_id, "priority": priority}
    return TASKS[new_id]

def create_tasks(items: list[dict]) -> list[dict]:
    """Create several tasks at once. Either all are created or none are.

    Every item is validated before any task is created, so one invalid
    item rejects the whole batch.

    Args:
        items: Task fields, each a dict with title, user_id, and an
            optional priority (defaults to 3 when the key is omitted).

    Returns:
        The newly created task records, in the same order as items.

    Raises:
        ValidationError: If an item is not an object, is missing title or
            user_id, or has an invalid title or priority. The message
            starts with "Item <index>: ".
        NotFoundError: If an item's user_id doesn't match a user. The
            message starts with "Item <index>: ".
    """
    for index, item in enumerate(items):
        try:
            if not isinstance(item, dict):
                raise ValidationError("item", "must be an object")
            for field in ("title", "user_id"):
                if field not in item:
                    raise ValidationError(field, "is required")
            _validate_new_task(item["title"], item["user_id"],
                               item.get("priority", DEFAULT_PRIORITY))
        except AppError as e:
            # Update args too so str(e) matches the message.
            e.message = f"Item {index}: {e.message}"
            e.args = (e.message,)
            raise

    # All items are valid, so nothing below can fail partway through.
    return [create_task(item["title"], item["user_id"],
                        item.get("priority", DEFAULT_PRIORITY))
            for item in items]

# Keyword-only (*) so callers must name the filter, e.g. list_tasks(priority=5);
# a bare list_tasks(5) could be mistaken for a user ID.
def list_tasks(*, user_id: int | None = None,
               priority: int | None = None) -> list[dict]:
    """Retrieve tasks, optionally filtered by user, priority, or both.

    Args:
        user_id: If given, only tasks owned by this user are returned.
        priority: If given, only tasks with this priority are returned.

    Returns:
        A list of task records matching every filter given, sorted by
        priority (1 first), with ties in ID order. Empty if no tasks match.

    Raises:
        NotFoundError: If user_id is given and no user exists with that ID.
        ValidationError: If priority is given and is not an integer
            between 1 and 5.
    """
    if user_id is not None and user_id not in USERS:
        raise NotFoundError("User")
    if priority is not None:
        _validate_priority(priority)
    matches = [task for task in TASKS.values()
               if (user_id is None or task["user_id"] == user_id)
               and (priority is None or task["priority"] == priority)]
    # sorted() is stable and TASKS is in ID order, so ties stay in ID order.
    return sorted(matches, key=lambda task: task["priority"])

def update_task_priority(task_id: int, priority: int) -> dict:
    """Update a task's priority.

    Args:
        task_id: The unique identifier for the task.
        priority: The new priority, from 1 to 5.

    Returns:
        The updated task record.

    Raises:
        NotFoundError: If no task exists with the given ID.
        ValidationError: If priority is not an integer between 1 and 5.
    """
    if task_id not in TASKS:
        raise NotFoundError("Task")
    _validate_priority(priority)
    TASKS[task_id]["priority"] = priority
    return TASKS[task_id]
