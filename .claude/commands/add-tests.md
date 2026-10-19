# Use this to add pytest tests for one existing function that has little or no test coverage; don't use it to build new features or fix bugs.

## Goal
Write pytest tests for one function. $ARGUMENTS has two values: the file, then the function name (for example: services/tasks.py get_tasks_by_status). Cover the happy path, every error listed in the function's docstring "Raises:" section, and edge cases like empty input or wrong types.

## Context
- Test style to follow: tests/test_tasks.py.
- For fixtures that reset in-memory data after each test, see tests/test_tags.py.
- The function's docstring says what it returns and what it raises.
- Errors are AppError subclasses from utils/errors.py. Check them with pytest.raises.

## Constraints
- Only create or edit tests/test_<module>.py (for services/tasks.py that's tests/test_tasks.py). Don't change the function or any file outside tests/.
- If a test fails because of a real bug in the function, don't fix the code. Stop and report the bug.
- Check the existing tests first and don't write duplicates.
- Reset any in-memory data you change (TASKS, USERS, TAGS) so tests don't affect each other.
- Use the Edit or Write tool to change test files, not a shell or Python script, so the project's hooks can check the write.

## Verification
Run pytest -q after adding the tests. All tests must pass. Report how many tests you added and the final pytest output.