# Task Manager

Python Flask API for managing tasks and users.

## Commands
- Install: pip install -r requirements.txt
- Run tests: python -m pytest -v
- Lint: python -m ruff check .

## Architecture
This project has three layers: routes -> services -> repositories.
- routes/api.py has the Flask routes. It catches AppError and turns it
  into the right HTTP response.
- services/ has the actual logic (services/tasks.py, services/users.py).
  Look at services/users.py as the example of how a service file should
  be written.
- There's no separate repository layer yet. Services just read and write
  the USERS and TASKS dictionaries directly.
- As confirmed through the Task 2 subagent decomposition: routes/api.py
  must call existing functions in services/users.py (e.g.,
  get_notification_pref, set_notification_pref) for validation rather
  than reimplementing it inline, SA-3 correctly followed this across
  all three new/updated routes.

## Conventions
- Every function needs type hints on its parameters and return value.
- Every function needs a Google-style docstring (Args/Returns/Raises),
  written the same way as services/users.py.
- When writing or changing a service function, copy the style of 
  services/users.py, including how it raises errors.
- Routes in routes/api.py must also avoid raw exceptions, check that
  required fields exist in the request body and raise ValidationError 
  if missing, instead of crashing with a KeyError.

## Do not touch
- Never raise a plain exception (like KeyError or Exception) from a
  service function. Always raise an AppError subclass from
  utils/errors.py instead (NotFoundError, ValidationError).
- Don't change the function signatures of get_task, create_task, or
  process_order in services/tasks.py, routes/api.py calls them directly.
- Don't add a database. USERS and TASKS are supposed to stay as
  in-memory dictionaries for this project.
- Do not create or modify files under tests/ while a session is scoped
  to services/users.py changes only, this was proposed once (during
  the notification-preference feature's service-layer work) and
  stopped before it happened.
- Do not create or modify files under tests/ while a session is scoped
  to routes/api.py changes only, this actually happened once (during
  the same feature's API-layer work, which wrote tests/test_users.py
  unprompted). It should be a separate, explicit step.