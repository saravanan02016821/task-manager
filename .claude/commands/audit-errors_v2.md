## Goal
  Audit $ARGUMENTS for missing AppError handling. This includes (1) explicit raises of raw exceptions (ValueError, TypeError, KeyError, Exception, etc.) and (2) implicit crashes, meaning operations that can throw a raw exception on bad input, such as calling string methods on a non-string, max()/min() on an empty collection, or dict[key] lookups. Replace explicit raw raises with the appropriate AppError subclass from utils/errors.py. For implicit crashes, add a guard that raises the appropriate AppError subclass instead, matching how _validate_priority in this file handles bad input.

## Context
- Canonical error-handling pattern: services/users.py
- AppError hierarchy: utils/errors.py (AppError, NotFoundError, BadRequestError, ValidationError)

## Constraints
- Do not modify utils/errors.py or any file outside $ARGUMENTS.
- Do not add new AppError subclasses — use only existing ones.
- Preserve all existing function signatures.

## Verification
Run pytest -q after every function you update. All existing tests must still pass before you move to the next function. Report the final pytest output when done.