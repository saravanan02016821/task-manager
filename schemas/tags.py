# Each field maps to its expected type and whether the request must include it.
TAG_SCHEMA: dict[str, dict] = {
    "name":  {"type": str, "required": True},
    "color": {"type": str, "required": False},
}
