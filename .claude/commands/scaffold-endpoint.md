## Goal
Scaffold a new API endpoint. $ARGUMENTS has two values: the resource name first, then the HTTP method (for example: tags POST). Create or update these three files:
- Route file: routes/api.py: add one new route for the resource and method.
- Service file: services/<resource>.py: create it if it doesn't exist, and put all the logic for this endpoint there.
- Schema file: schemas/<resource>.py: create it (and schemas/__init__.py) if it doesn't exist. It lists the resource's fields, which are required, and their types.

## Context
- Canonical pattern: routes/tasks.py. In this repo there is no separate routes/tasks.py — all routes live in routes/api.py, so follow the task routes there (GET /tasks, POST /tasks, PATCH /tasks/<id>).
- Service pattern: services/tasks.py and services/users.py (in-memory dicts, type hints, Google-style docstrings).
- Errors: raise AppError subclasses from utils/errors.py. handle_app_error in routes/api.py already turns them into JSON responses.

## Constraints
- No business logic in the route handler. The route only reads the request, calls one service function, and returns jsonify(result) with the status code.
- Reject a request body that isn't a JSON object (for example a list) with a ValidationError, instead of crashing.
- Store data in an in-memory dict, like TASKS and USERS. Don't add a database.
- Do not modify utils/errors.py, and don't change any existing endpoint or existing function signature.

## Verification
Add one happy-path test for the new endpoint in tests/test_<resource>.py. Run pytest -q. All existing tests must still pass, and the new endpoint must return the correct status code on the happy path: 201 for POST, 200 for GET/PATCH/PUT, 204 for DELETE. Report the final pytest output.
