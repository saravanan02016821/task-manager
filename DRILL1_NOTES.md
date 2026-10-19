# Drill 1 Notes

## Phase 1 — Recurring task
Check a services file and swap out raw exceptions for the right AppError class.

Why I picked this (from PLAN_LOG.md): In Session 3, process_order raised a KeyError and I
changed it to NotFoundError. In Session 5, I had to pick between BadRequestError (400) and
ValidationError (422). And in my Notes there's a bug where sending a title that isn't text
gives a 500 instead of a 422.

## Phase 2 — Command file
Made .claude/commands/audit-errors.md with Goal, Context, Constraints, and Verification.
Saved a copy as audit-errors_v1.md.

## Phase 3 — Run 1 (v1)
- Files edited: none
- Pytest ran: once at the end (64 passed). Nothing got changed, so the "run pytest after
  every function" step never happened.
- Scope: Pass. Didn't touch anything outside services/tasks.py.
- Pattern: Pass. Every raise in the file already used an AppError class, same as
  services/users.py (ValidationError, NotFoundError).
- Verification: Couldn't check it, since nothing was changed.
- Problem: the Goal was too narrow. "Raises a raw exception" made Claude only look for
  actual raise lines, so it missed two spots where the code can crash on its own:
  line 75 (title.strip() crashes with AttributeError if title isn't text — this is the
  500 bug from my PLAN_LOG Notes) and line 99 (max() on an empty TASKS crashes with
  ValueError). Claude just mentioned these as suggestions and didn't fix them.

## Change made for v2 (Goal)
- Changed the Goal so it also covers code that can crash on its own (like .strip() on
  something that isn't text, or max() on an empty list), and told Claude to handle it
  the same way _validate_priority does. Saved as audit-errors_v2.md.

## Phase 3 — Run 2 (v2)
- Files edited: only services/tasks.py (4 functions: _validate_new_task, create_tasks,
  list_tasks, create_task).
- Pytest ran: after every function (4 times, 64 passed each time), plus once at the end
  (64 passed). Ruff was clean.
- Scope: Pass. Only services/tasks.py changed. I told it to skip the task ID checks (#6).
- Pattern: Pass. It used ValidationError (422) for wrong-type input, same as
  _validate_priority, and updated the "Raises:" part of each function's docstring.
- Verification: Pass. Pytest ran after each function like v2 says. (Couldn't check this
  in Run 1 since nothing changed.)
- Result: the 500 bug from my PLAN_LOG Notes ({"title": 123}) now gives a 422
  ValidationError instead.
- Things Claude pointed out that are still left:
  1. {"title": 123} says "Invalid title: cannot be empty", which is kind of confusing for a number.
  2. There are no new tests for the new checks. All 64 tests passed, but none of them test
     these cases yet.

## Phase 4 — users.py test
- First try (v2): FAIL. Claude didn't actually edit anything (it asked me first), but it
  wanted to change 3 functions in services/users.py (get_user, create_user,
  get_notification_pref). It found 5 spots that could crash, even though users.py is the
  reference file that's supposed to already be right.
- Why: v2 made the audit look for code that can crash on its own, and my Constraints
  didn't say "skip code that's already fine" or "users.py is the reference, don't change it."
- Also: v2 said "_validate_priority in this file," which only makes sense for tasks.py.
  Claude noticed that.
- I said no to the changes, and fc showed users.py didn't change.

## Change made for v3 (Constraints + Goal fix)
- Goal: changed "_validate_priority in this file" to "_validate_priority in services/tasks.py".
- Constraints: added two rules:
  1. If a function already uses the right AppError class, skip it — don't rewrite,
     reformat, or change its docstring.
  2. services/users.py is the reference file. If it's the target, just say
     "No changes needed — this is the reference file" and stop.
- Saved as audit-errors_v3.md.

## Phase 4 — Re-runs
- Re-run 1: it still wanted to make changes. Turns out I never saved my edit, so Claude
  read the old 14-line file.
- Re-run 2 (v3, saved this time, 17 lines): PASS. Claude said "No changes needed — this is
  the reference file" and stopped without auditing, editing, or running pytest.
- Note: it passed because of the rule that's just about users.py, so it never got to the
  general "skip functions that already use AppError correctly" rule. I haven't really
  tested that general rule on its own yet.

## Debrief

### Q1

I changed the Goal. v1 said to fix functions that "raise a raw exception," so Claude only
looked for actual raise lines. It didn't find any in services/tasks.py, so it didn't change
anything. Because of that, it missed the 500 bug from my PLAN_LOG Notes (title.strip() on
something that isn't text, line 75). In v2, I changed the Goal to also cover code that can
crash on its own, like .strip() on non-text or max() on an empty list, and told Claude to
handle it the same way _validate_priority does. In Run 2, it found 5 spots, fixed 4
functions, and ran pytest after each one (64 passed every time). Then in Phase 4 I had to
make a v3 change to the Constraints, because the bigger v2 Goal made Claude want to "fix"
the reference file too.

### Q2

CLAUDE.md gets loaded in every session, so it's for rules that always apply, like "never
raise raw exceptions." A slash command only runs when I call it, for one specific job, and
'$ARGUMENTS' lets me point it at a different file each time. If I put the whole audit in
CLAUDE.md, it would show up in every session even when I'm doing something else, and I
couldn't give it a file to check. As a command, the whole Goal/Context/Constraints/
Verification runs the same way every time from one line, and I could keep improving it
from v1 to v3 without messing with the project's main rules.

### Q3

Not at first. With v2, Claude wanted to change 3 functions in users.py, even though that's
the reference file. It didn't actually edit anything since it asked me first. That showed
my Constraints only said where Claude could make changes, not when it should leave good
code alone. Making the Goal bigger in v2 made this worse. Claude also pointed out that
"_validate_priority in this file" only made sense for tasks.py. In v3, I added two
Constraints: a general "skip it if it's already right" rule, and a rule saying users.py is
the reference so just say no changes are needed and stop. After that, Claude stopped right
away. What I learned is that Constraints need to tell Claude to leave correct code alone,
not just which files it can touch. Since v3 passed because of the users.py rule, I still
need to test the general "skip it" rule on another file that's already correct.