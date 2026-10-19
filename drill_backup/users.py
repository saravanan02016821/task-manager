from utils.errors import NotFoundError, ValidationError

NOTIFICATION_PREFS: tuple[str, ...] = ("email", "sms", "none")

USERS: dict[int, dict] = {
    1: {"id": 1, "name": "Alice", "email": "alice@example.com", "notification_pref": None},
    2: {"id": 2, "name": "Bob",   "email": "bob@example.com",   "notification_pref": None},
}

def get_user(user_id: int) -> dict:
    """Retrieve a user by ID.

    Args:
        user_id: The unique identifier for the user.

    Returns:
        The user record as a dictionary.

    Raises:
        NotFoundError: If no user exists with the given ID.
    """
    if user_id not in USERS:
        raise NotFoundError("User")
    return USERS[user_id]

def create_user(name: str, email: str) -> dict:
    """Create a new user.

    Args:
        name: The user's display name.
        email: The user's email address.

    Returns:
        The newly created user record, with notification_pref set to None.

    Raises:
        ValidationError: If name or email is empty.
    """
    if not name or not name.strip():
        raise ValidationError("name", "cannot be empty")
    if not email or "@" not in email:
        raise ValidationError("email", "must be a valid email address")
    new_id = max(USERS.keys()) + 1
    USERS[new_id] = {"id": new_id, "name": name, "email": email, "notification_pref": None}
    return USERS[new_id]

def get_notification_pref(user_id: int) -> str:
    """Retrieve a user's notification preference.

    Args:
        user_id: The unique identifier for the user.

    Returns:
        The user's notification preference: "email", "sms", or "none".
        A stored value of None is returned as "none".

    Raises:
        NotFoundError: If no user exists with the given ID.
    """
    user = get_user(user_id)
    return user["notification_pref"] or "none"

def set_notification_pref(user_id: int, pref: str | None = None) -> dict:
    """Set a user's notification preference.

    Args:
        user_id: The unique identifier for the user.
        pref: One of "email", "sms", or "none". None or omitted is
            treated as "none".

    Returns:
        The updated user record.

    Raises:
        NotFoundError: If no user exists with the given ID.
        ValidationError: If pref is not an allowed value.
    """
    if pref is None:
        pref = "none"
    if pref not in NOTIFICATION_PREFS:
        raise ValidationError("notification_pref", "must be one of: email, sms, none")
    user = get_user(user_id)
    user["notification_pref"] = pref
    return user
