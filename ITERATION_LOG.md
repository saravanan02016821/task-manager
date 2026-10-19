## Session 1 - 10/2/26

### Prompt used
Add error handling to the get_task function in @services/tasks.py. Do not change the function signature. Run pytest -v when done.

### What Claude did
Claude changed get_task in services/tasks.py to raise NotFoundError("Task") from utils/errors.py instead of letting a bare KeyError escape, matching the same pattern get_user uses in services/users.py. It added a docstring and kept the overall function signature unchanged, as instructed. It also updated the test_get_task_invalid in tests/test_tasks.py to expect NotFoundError instead of a generic exception. All 4 tests passed and ruff reported no issues. Claude also pointed out that process_order still raises a plain KeyError and has no docstring, which breaks the Conventions rules, but left it alone since it wasn't part of this prompt.

### Observation
The Conventions and Do-not-touch rules governed this session and were followed exactly for get_task: no raw exceptions, AppError was used instead, a proper docstring, type hints preserved. But this also did show that there was a limitation: CLAUDE.md states a project-wide standard ("never raise raw exceptions"), but Claude only does it on the function it's actively editing. process_order still violates that same rule and was left untouched. CLAUDE.md doesn't get swept across the whole codebase automatically, only applied file-by-file as each function gets touched.

### CLAUDE.md update (if any)
No change made yet. I'm holding off on an update until I see whether this same gap shows up again in later sessions.

---------------------------------------------------------------------

## Session 2 - 10/2/26

### Prompt used
Refactor create_task in @services/tasks.py to match the style of get_user in @services/users.py exactly. Run pytest -v when done.

### What Claude did
Claude changed create_task so it checks for problems before doing anything else. If the title is empty, it raises ValidationError. If the user_id doesn't exist, it raises NotFoundError. It also added a Google-style docstring like get_user has. The function signature didn't change. All 4 tests still passed and ruff found no problems.

Claude also tested create_task by hand, since the test file doesn't actually have any tests for create_task. It found that creating a task for a user who doesn't exist now correctly fails with a 404 error, instead of silently working like it used to.

Claude also noticed something on its own: if someone sends a request with no title or user_id at all, the app still crashes with a plain 500 error. This happens because routes/api.py grabs data["title"] from the request before create_task is ever called. CLAUDE.md's rule about using AppError only talks about service functions, not the routes file, so this bug is still there.

### Observation
The Conventions rule worked well for create_task itself and it now matches get_user's style and uses the right error types. But this session showed a real gap: CLAUDE.md's error handling rule only covers service functions, so it doesn't stop routes/api.py from crashing on bad input before a service function even runs. This is a case where CLAUDE.md didn't prevent a real mistake, because the rule was written too narrow.

### CLAUDE.md update
I added a new rule under Conventions:
"Routes in routes/api.py must also avoid raw exceptions check that required fields exist in the request body and raise ValidationError if they're missing, instead of crashing with a KeyError."
I added this because Session 2 showed that a missing title or user_id still causes a 500 error, and the old rule did not apply to it.

--------------------------------------------------------------------------

## Session 3 - 10/2/26

### Prompt used
Add a new function to @services/tasks.py that returns all tasks for a given user_id. Follow the same pattern as the existing functions. Add a test for it. Run pytest -v when done.

### What Claude did
Claude added a new function, get_tasks_for_user, to services/tasks.py. It has a Google-style docstring, type hints, and raises NotFoundError if the user doesn't exist, matching the pattern from get_user and get_task. It returns an empty list if the user exists but has no tasks. Claude also added two tests for it in tests/test_tasks.py: one checking it works for a real user, one checking it raises NotFoundError for a user that doesn't exist. All 6 tests passed and ruff found no problems. Claude didn't add an API route for it, since the prompt didn't ask for one, but mentioned that the new routing rule from Session 2 would apply if one were added later.

### Observation
This session followed CLAUDE.md's rules correctly with no corrections needed from me at all, good docstring, right error type, tests included. Compared to Session 1 (needed a test file update) and Session 2 (found a real bug CLAUDE.md didn't cover), this session needed the least amount of cleanup. This would be a sign that the rules are doing their job better the more they get used.

### CLAUDE.md update
I added a new rule under Conventions:
"New functions added to services/tasks.py or services/users.py must come with matching tests in tests/."
I added this because Session 2's create_task had no tests written for it at all. This rule makes sure that gap doesn't happen again going forward.