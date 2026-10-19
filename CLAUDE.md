# Task Manager

Python Flask API for managing tasks and users.

## Commands
- Install: pip install -r requirements.txt
- Run tests: python -m pytest -v
- Lint: python -m ruff check .
- Start Claude Code from inside the task-manager folder, otherwise it won't load the slash commands or the hook below.
- `/audit-errors <file>` (e.g. `/audit-errors services/tasks.py`): checks one services file for raw exceptions and code that can crash on bad input, and swaps in the right AppError subclass; skips functions that are already correct and never touches utils/errors.py.
- `/scaffold-endpoint <resource> <METHOD>` (e.g. `/scaffold-endpoint tags POST`): adds a new endpoint with the route in routes/api.py, the logic in services/<resource>.py, the fields in schemas/<resource>.py, and a happy-path test.
- `/add-tests <file> <function>` (e.g. `/add-tests services/tasks.py get_tasks_by_status`): writes pytest tests for one existing function, covering the happy path, its errors, and edge cases; only touches files in tests/.

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
- Do not create or modify files under tests/ while a session is scoped
  to services/users.py changes only, this was proposed once (during
  the notification-preference feature's service-layer work) and
  stopped before it happened.
- Do not create or modify files under tests/ while a session is scoped
  to routes/api.py changes only, this actually happened once (during
  the same feature's API-layer work, which wrote tests/test_users.py
  unprompted). It should be a separate, explicit step.

## Hooks
`.claude/hooks/guard_writes.py` is a PreToolUse hook (registered in `.claude/settings.json` with the matcher `Write|Edit|MultiEdit|Bash`) that runs before every file write and shell command, and blocks it with exit code 2 if it breaks a rule. It blocks writes to `utils/errors.py`, `migrations/`, `.env`, and `.claude/settings.json` (through the Write/Edit/MultiEdit tools or through Bash, and no matter the capital letters); it blocks the shell commands `DROP TABLE`/`TRUNCATE TABLE`, `rm -rf`, and `git push --force`; and it blocks hardcoded database connection strings (`postgresql://`, `sqlite:///`) in `services/tasks.py`, which together with the `migrations/` block is how the "no database" rule is enforced. To add a rule, open the script and add the path (relative to the repo root, ending in `/` for a folder) to `BLOCKED_PATHS`, add a `(regex, message)` pair to `BLOCKED_COMMANDS` for a shell command (use `\b` word boundaries so it doesn't match parts of other words), or add a file to `CONTENT_GUARDED_FILES` to scan what gets written into it. Then test it by piping a fake tool call into the script, e.g. `echo {"tool_name":"Edit","tool_input":{"file_path":"utils/errors.py"}} | python .claude\hooks\guard_writes.py` followed by `echo %errorlevel%` (2 = blocked, 0 = allowed), check that a normal file still gives 0, and run `python -m py_compile .claude\hooks\guard_writes.py` and `python -m pytest -q`, because a hook with a Python error exits with 1 and quietly lets everything through.