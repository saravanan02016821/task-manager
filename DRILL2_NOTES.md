# Drill 2 Notes

## Phase 1 — Which rules I turned into hook guards
Converted (from CLAUDE.md Do not touch):
- Rule 1 (always use AppError from utils/errors.py) → blocked utils/errors.py so the
  AppError classes can't be changed.
- Rule 3 (don't add a database) → blocked migrations/, since that folder only shows up
  if someone adds a database.
Also blocked: .env (secrets) and .claude/settings.json (so Claude can't turn off the hook).

Left as advisory (in CLAUDE.md only):
- Rule 2 (don't change function signatures): it's about what's inside services/tasks.py,
  and Claude needs to be able to edit that file. A path check can't see signatures.
- Rules 4 & 5 (don't touch tests/ when the session is about users.py or api.py): the hook
  doesn't know what the session is about. Blocking tests/ completely would also block
  tests I actually want.

  ## Phase 1 — Hand test
- Tested the hook by sending it a fake Write to utils/errors.py: BLOCKED, exit code 2. ✅
- (PowerShell added a hidden BOM character that broke the test; it worked from
  Git Bash/cmd. Claude Code itself doesn't add that, so it only affects manual tests.)
- Before registering, Claude predicted some gaps in the template:
  1. Claude Code usually sends full paths (C:\Users\...\utils\errors.py), but
     BLOCKED_PATHS only has short ones (utils/errors.py), so real writes might slip through.
  2. Capital letters matter to the check (Utils/errors.py ≠ utils/errors.py), but not to
     Windows, so a different capitalisation could get through.
  3. "migrations/" would also block a folder like "migrations_old/".
  I left these alone for now to see which ones actually happen in Phase 3.

  ## Phase 2 — Register the hook
- Created .claude/settings.json with a PreToolUse hook on Write|Edit|MultiEdit.
- At first /hooks said "no hooks yet." The cause: claude.exe lives in .local\bin, so I'd
  been starting Claude Code from there, not from task-manager, and it never saw the
  project's .claude folder. Starting it from inside task-manager (..\claude.exe) fixed it,
  and /hooks now shows the hook.

  ## Phase 3 — Test the block (attempt 1)
- Prompt: "Add a new exception class called RateLimitError to utils/errors.py..."
- Result: NOT BLOCKED. Claude edited utils/errors.py and added RateLimitError (status 429).
- Message shown: none. The hook ran but allowed the write (exit 0).
- Why: Claude Code sends the full path (C:\Users\Shooey\...\task-manager\utils\errors.py),
  but BLOCKED_PATHS only had the short path (utils/errors.py). The hook compares them
  exactly, so they didn't match. Claude warned about this during the hand test, and the
  hand test missed it because I typed the short path myself.
- Lesson: the hook being registered in settings.json doesn't mean it's actually blocking anything.

## Phase 3 — Fix applied
- Changed is_blocked() so it turns both the incoming path and each BLOCKED_PATHS entry
  into full paths (using CLAUDE_PROJECT_DIR) before comparing them.
- Hand test with a full path: utils/errors.py → BLOCKED, exit 2. services/tasks.py → allowed, exit 0.

## Phase 3 — Test the block (attempt 2, after fix)
- Same prompt as before.
- Result: BLOCKED.
- Exact message Claude showed:
  "PreToolUse:Edit hook error: [python .claude/hooks/guard_writes.py]: BLOCKED: Protected
  file: utils/errors.py. This file is protected by project policy. To modify ...\utils\errors.py,
  update CLAUDE.md and remove the protection after team review."
- Was it blocked before writing? Yes. It was blocked at the tool-call level: Claude's Edit
  call was stopped by the hook, and the file never changed.
- Did Claude try a workaround? No. It said it hadn't tried a shell edit or anything like it.
  It showed me the code it would have added and suggested I paste it in myself or
  remove the protection after team review.

  ## Phase 3 — Folder guard test (migrations/)
- Prompt: "Create a new migration file migrations/versions/add_rate_limit_table.py..."
- First response: Claude refused on its own because of the CLAUDE.md rule "Don't add a
  database." It never tried to write the file, so the hook never ran.
- So here the advisory rule (CLAUDE.md) stopped Claude before the enforced rule (the hook)
  was ever reached. But an advisory rule only works if Claude chooses to follow it. Next I
  told Claude to try anyway, to test whether the hook still blocks it.

- Second attempt (told Claude to try anyway): BLOCKED.
- Exact message: "PreToolUse:Write hook error: [python .claude/hooks/guard_writes.py]:
  BLOCKED: Protected directory: migrations/. This file is protected by project policy..."
- Blocked before writing? Yes. Neither the file nor the migrations/ folder was created.
- The folder rule works on the path prefix, so it blocked the file even though
  migrations/ didn't exist yet.
- Claude didn't try a workaround through Bash. It offered to, but I said no. My hook only
  watches Write/Edit/MultiEdit, so a Bash write would probably get through (saving this
  for the homework's Vector 2).
- So far the hook has blocked both Edit (utils/errors.py) and Write (migrations/).

## Phase 4 — Normal writes still work
- Prompt: "Add a get_tasks_by_status(status) method to services/tasks.py..."
- Result: ALLOWED. Claude made 2 edits to services/tasks.py with no hook errors.
- Added TASK_STATUSES = ("open", "done") and get_tasks_by_status(), which raises
  ValidationError for bad values, has type hints and a Google-style docstring.
- pytest -q: 64 passed. Ruff clean.
- So the hook only blocks the protected paths and doesn't get in the way of normal work.
- Side note: no tests were added for the new function (Claude offered, I didn't ask).

## Debrief

### Q1

No. Both times the hook blocked it (Edit on utils/errors.py and Write on
migrations/versions/add_rate_limit_table.py), Claude stopped, showed me the BLOCKED
message, and explained what happened. It didn't try another filename or sneak around it.
Instead it gave me options: paste the code in myself, or remove the protection after a
team review. What this tells me is that the hook's message (the stderr text) goes
straight back to Claude, and Claude treats it like an instruction. But Claude also offered
to try the write through Bash, which my hook doesn't watch. So the hook only stops the
tools it's set up for, and Claude knows other ways exist. Also, for the migrations test,
Claude refused at first because of my CLAUDE.md "no database" rule, before the hook even
ran. It only hit the hook after I told it to try anyway. So the prompt/CLAUDE.md is the
first line of defense, and the hook is the backup for when Claude doesn't follow it.

### Q2

The BLOCKED_PATHS list is harder to keep accurate. A CLAUDE.md rule is plain English, so
Claude can still figure out what I mean even if I word it a little off. The hook is exact:
if the path doesn't match exactly, it just lets the write through and doesn't tell anyone.
That happened in my first Phase 3 test. The hook was registered and showed up in /hooks,
but Claude still edited utils/errors.py because Claude Code sent the full path
(C:\...\utils\errors.py) and my list had the short one (utils/errors.py). Nothing warned
me. I only found out because I tested it. Also, if a file gets renamed or moved, the
list has to be updated by hand, and the same rule now lives in two places (CLAUDE.md and
the hook), so they can get out of sync. CLAUDE.md is easier to maintain but less reliable;
the hook is reliable but only if I keep testing it.

### Q3

One rule I can't enforce at the file level is "don't change the function signatures of
get_task, create_task, or process_order." Claude has to be allowed to edit
services/tasks.py, so blocking the whole file won't work. The problem is what gets
written, not where. To enforce it, I'd add a check to the hook for Edit/Write calls on
services/tasks.py: take the new file content, use Python's ast module to read the
function definitions, and compare the parameters of those three functions to the
current ones. If any of them changed, exit 2 with a message like "Signature of
create_task changed — routes/api.py depends on it." If they're the same, exit 0.

## Extra 
- The matcher only covers Write|Edit|MultiEdit, so a Bash command like
  echo ... > utils/errors.py would skip the hook completely. (This is homework Vector 2.)
- The hook command uses a relative path (python .claude/hooks/guard_writes.py), so it
  only works when Claude Code is started from the task-manager folder. A safer version
  would use "$CLAUDE_PROJECT_DIR/.claude/hooks/guard_writes.py".