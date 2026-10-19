# Week 6 Retrospective

## 1. Slash command value

`/scaffold-endpoint` saved me the most prompt-writing (COMMAND_LOG.md, row 2: `/scaffold-endpoint tags POST`).
One line got me `schemas/tags.py`, `services/tags.py`, `tests/test_tags.py`, and a new route in
`routes/api.py`, with a passing test that got a 201 (65 passed). Without the command I'd have to type
something like: "Add a POST /tags endpoint. Put the route in routes/api.py and follow the task routes
there, put the logic in a new services/tags.py with an in-memory dict like TASKS, make a schemas/tags.py
with the fields, don't put any logic in the route, reject a body that isn't a JSON object, don't add a
database, don't touch utils/errors.py, add a happy-path test, and run pytest and check it returns 201."
That's a lot to remember every time, and I'd probably forget at least one piece, like the "body must be
an object" rule, which only exists because Claude found that a list body crashed `routes/api.py` with a
500. The command is also better because when I fix it, the fix sticks: after the first run added a
duplicate-name check I never asked for, I added a Constraint about it once, and every future run gets it.

## 2. Hook reliability

Both bypass vectors got past my hook before I fixed them (HOOK_LOG.md, Part B). In Vector 1, Prompt 2
edited `Utils/errors.py` (capital U) with no hook output, because the hook compared paths letter by
letter and Windows treats `Utils` and `utils` as the same folder. In Vector 2, Prompt 2 ran
`echo "# written from bash" >> utils/errors.py` and it went through, because the Bash branch only looked
for things like `rm -rf` and never checked which file a command writes to. That wasn't the only time.
In Drill 2, `/hooks` showed the hook as registered, but Claude still edited `utils/errors.py` because
Claude Code sends full paths and my list had short ones. And when I broke the indentation while fixing
Vector 2, the hook crashed with exit code 1, which Claude Code treats as "allow," so for a bit nothing
was blocked at all. What this shows is that "the rule is in settings.json" only means the script runs.
Whether anything actually gets blocked depends on the matcher and the matching code, and the only way to
know is to actually try to break it.

## 3. Advisory vs. deterministic

The rule I left advisory is the one in CLAUDE.md's Do-not-touch section about not creating or changing
files under `tests/` when a session is only supposed to be about `services/users.py` or `routes/api.py`.
I didn't move it into `guard_writes.py` because the hook only sees a file path. It has no idea what the
session is "about." If I just blocked all of `tests/`, I'd also block `/add-tests` and
`/scaffold-endpoint`, which are supposed to write tests (COMMAND_LOG.md rows 2 and 3). The condition for
graduating it: this has already happened once (during the notification-preference API work, Claude wrote
`tests/test_users.py` without being asked), so the next time Claude writes to `tests/` in a session where
I didn't ask for tests, I'll add `tests/` to `BLOCKED_PATHS` and have the hook allow test writes only
when I start Claude with an environment variable like `ALLOW_TEST_WRITES=1`, which I'd set for
`/add-tests` and `/scaffold-endpoint` sessions.

## 4. Limits of hooks

I wanted to enforce "all tests have to pass after every change." That's in my `/audit-errors`
Verification ("run pytest -q after every function"), but it's only a request. Claude followed it in Drill
1 Run 2, but nothing forces it. I couldn't do this with a PreToolUse hook, because PreToolUse runs
*before* the edit happens. At that point the change isn't in the file yet, so there's nothing to test,
and the hook can only say yes or no to the edit itself. The right tool would be a PostToolUse hook on
Write/Edit/MultiEdit (and Bash, since `/add-tests` wrote through Bash) that runs `python -m pytest -q`
right after the change and sends any failures back to Claude so it has to fix them, plus a CI check on
the repo so nothing broken gets merged even if a hook gets skipped.