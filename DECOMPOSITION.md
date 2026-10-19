# Subagent Decomposition — Notification Preference Feature

| Field | SA-1: Data layer | SA-2: Service layer | SA-3: API layer | SA-4: Tests |
|---|---|---|---|---|
| **Input** | `services/users.py` | `services/users.py` (after SA-1), `utils/errors.py` | `routes/api.py`, `services/users.py` (after SA-2) | Full repo (after SA-3), `tests/test_tasks.py` for style |
| **Task** | Add a `notification_pref` field to users (nullable, defaults to `None`), without changing `create_user`'s signature | Add `get_notification_pref(user_id)` and `set_notification_pref(user_id, pref)` pref has to be `email`, `sms`, `none`, or `None` | Add the two new routes (`PATCH`/`GET` `/users/{id}/notifications`), and make `GET /users/{id}` include `notification_pref` too | Write tests for all of it, good/bad PATCH values, the GET route, and that `notification_pref` shows up in the user detail response |
| **Output** | `services/users.py` | `services/users.py` | `routes/api.py` | `tests/test_users.py` (new file) |
| **Constraint** | Can't touch `routes/api.py` or add routes | Can't touch `routes/api.py`; can't change `create_user`'s or `get_user`'s signatures | Can't touch the validation logic inside `services/users.py` just call what SA-2 made | Can't touch `services/users.py` or `routes/api.py` |
| **Hand-off** | Every user has a `notification_pref` key (even if it's `None`) so SA-2 has something to read/write | The exact function names (`get_notification_pref`, `set_notification_pref`) and the exact error message format SA-3's routes will pass straight through | The two route paths + response shapes, so SA-4 knows exactly what to test | last one, nothing to hand off |

## SA-1: Data Layer
Goal: Add a notification_pref field to the User model.
Context: See @services/users.py. Field is nullable, defaults to
None, one of "email", "sms", "none", or None.
Constraints: Do not change create_user's or get_user's signatures.
Do not touch routes/api.py.
Verification: Run pytest -q when done (expect no new tests yet,
just no breakage).

**Result:** Pass 51/51 tests, lint clean. Constraints honored
(routes/api.py untouched, signatures unchanged). Asked whether to
add the setter now; told it no, defer to SA-2. Note: a persistent
memory file survived /clear and made it plan-first instead of
editing directly, see Divergence section below for detail.


## SA-2: Service Layer
Goal: Add get_notification_pref(user_id) and
set_notification_pref(user_id, pref) to the user service.
Context: See @services/users.py (after SA-1's change adding
notification_pref). pref must be one of "email", "sms", "none",
or None/omitted (treated as "none"). Reuse ValidationError from
@utils/errors.py for invalid values, following the pattern used
elsewhere in this file.
Constraints: Do not touch routes/api.py. Do not change
create_user's or get_user's existing signatures.
Verification: Run pytest -q when done.

**Result:** Pass 51/51 tests (unchanged, no new tests added as
instructed), lint clean. Constraints honored (routes/api.py
untouched, signatures unchanged, test file deferred to SA-4). Note:
SA-2's prompt didn't explicitly forbid writing tests, Claude
initially proposed creating tests/test_users.py on its own, which I
caught and deferred to SA-4. Manually verified getter/setter
behavior via shell (strict matching, 404 for unknown user, 422 for
bad values, None -> "none") since no automated tests exist yet.


## SA-3: API Layer
Goal: Add PATCH /users/{id}/notifications and
GET /users/{id}/notifications routes. Also update the existing
GET /users/{id} route so its response includes notification_pref.
(There's no GET /users list route in this repo, just the
single-user one, so that's the only existing route to update.)
Context: See @routes/api.py and @services/users.py (after SA-2's
get_notification_pref / set_notification_pref functions exist,
call those directly instead of rewriting validation here).
Constraints: Do not touch the validation logic inside
services/users.py, only call the functions SA-2 made. Do not
change any existing route's path or method.
Verification: Run pytest -q when done.

**Result:** Pass 64 tests (51 + 13 new), lint clean. Constraints
honored (services/users.py untouched, no existing route path/method
changed). Caught a real bug before approving: plan initially stated
wrong status codes (400 instead of 422) due to confusing AppError's
default with ValidationError's fixed value, I flagged it, Claude
verified against utils/errors.py and existing tests, corrected the
plan. Self-caught during execution: first test run used URLs
without the /api blueprint prefix, got 10 false 404s; fixed by
correcting the test URLs, no route code changed.


## SA-4: Tests
Goal: Add tests for the notification preference feature: good and
bad PATCH values, GET returning the right preference, and that
GET /users/{id} includes notification_pref.
Context: See @routes/api.py and @services/users.py (final state
after SA-1–SA-3), and @tests/test_tasks.py for the test style to
match. There are no user tests yet, make a new file
tests/test_users.py for these.
Constraints: Do not touch services/users.py or routes/api.py,
tests only. Do not touch tests/test_tasks.py.
Verification: Run pytest -q when done.

## SA-4: Tests
Not executed as a separate session. SA-3 wrote tests/test_users.py
itself (13 tests covering GET/PATCH, valid/invalid values, 404s)
before I could run this step. See Divergence section for details.