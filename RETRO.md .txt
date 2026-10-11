# Retro.md

## 1. Plan Mode value

In Session 1 (PLAN_LOG.md), amending the plan prevented a real problem: Claude's first draft would have changed `create_task`'s signature to add `priority`, directly violating a rule already in CLAUDE.md's "Do not touch" section (no signature changes to `get_task`, `create_task`, or `process_order`). Because I caught this at the plan stage and told Claude to use an optional keyword argument defaulting to 3 instead, I never had to revert any code, the fix happened before a single line was written.

## 2. Plan Mode limits

Session 7's divergence is the clearest example of where Plan Mode's reliability runs out. The plan for `POST /tasks/bulk` correctly described the intended behavior, prefix each validation error with "Item N:" by mutating the exception's `.message` and re-raising it. But the first implementation attempt failed 2 tests, because `pytest.raises(match=...)` actually reads an exception's `args`, not its `.message` attribute, a Python-level detail the plan had no way to anticipate since it operates at the level of what the code should do, not how a specific test assertion inspects an exception object. This shows the boundary of what Plan Mode can supervise: it catches design-level mistakes (wrong error class, wrong status code, a missing endpoint) but not execution-level details that only surface once code actually runs against real test machinery.

## 3. Subagent value

The most important boundary to enforce was the one that nearly broke twice: a subagent writing to `tests/` while scoped to a different layer. SA-2 (scoped to `services/users.py`) proposed creating `tests/test_users.py` on its own, I caught it and deferred that work to SA-4. SA-3 (scoped to `routes/api.py`) did it anyway, writing `tests/test_users.py` with 13 tests before SA-4 ever ran. If I'd let Claude implement this whole feature in one session instead of decomposing it, there would have been no natural stopping point to catch a related mistake, SA-3 initially described the wrong status code (400 instead of 422) for validation errors, confusing `AppError`'s default with `ValidationError`'s actual fixed value. In a single session, that mistake could have been written directly into both the code and self-written tests with nothing forcing a pause to check it against the real contents of `utils/errors.py`.

## 4. Gap analysis

Both Plan Mode and subagent decomposition are advisory, they rely on me reading carefully and catching things, which is exactly what went wrong twice with the tests/ boundary. The specific rule I'd most want enforced mechanically is: a subagent session should only be able to write to files listed in its own Output field. A hook that enforces it would block any Write or Edit tool call whose target file path isn't on a pre-declared allowlist for that session.