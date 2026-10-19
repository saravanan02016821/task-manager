from schemas.tags import TAG_SCHEMA
from utils.errors import ValidationError

TAGS: dict[int, dict] = {}

def _validate_new_tag(data: object) -> None:
    """Check that the fields for a new tag match TAG_SCHEMA.

    Args:
        data: The parsed JSON request body.

    Raises:
        ValidationError: If data is not an object, a required field is
            missing, a field has the wrong type, name is empty, or a tag
            with the same name (ignoring case) already exists.
    """
    if not isinstance(data, dict):
        raise ValidationError("body", "must be a JSON object")
    for field, rules in TAG_SCHEMA.items():
        if field not in data:
            if rules["required"]:
                raise ValidationError(field, "is required")
            continue
        if not isinstance(data[field], rules["type"]):
            raise ValidationError(field, f"must be a {rules['type'].__name__}")
    name = data["name"].strip()
    if not name:
        raise ValidationError("name", "cannot be empty")
    if any(tag["name"].lower() == name.lower() for tag in TAGS.values()):
        raise ValidationError("name", "already exists")

def create_tag(data: object) -> dict:
    """Create a new tag from a request body.

    Args:
        data: The parsed JSON request body. Must be an object with a
            name and an optional color. Unknown fields are ignored.

    Returns:
        The newly created tag record. color is None when not given.

    Raises:
        ValidationError: If data is not an object, name is missing, empty,
            or already used, or a field has the wrong type.
    """
    _validate_new_tag(data)
    new_id = max(TAGS, default=0) + 1
    TAGS[new_id] = {"id": new_id, "name": data["name"].strip(),
                    "color": data.get("color")}
    return TAGS[new_id]
