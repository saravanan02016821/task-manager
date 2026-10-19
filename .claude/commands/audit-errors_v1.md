## Goal
Audit $ARGUMENTS for missing AppError handling. For every function that raises a raw exception (ValueError, TypeError, KeyError, Exception, etc.), replace it with the appropriate AppError subclass from utils/errors.py.

## Context
- Canonical error-handling pattern: services/users.py
- AppError hierarchy: utils/errors.py (AppError, NotFoundError, BadRequestError, ValidationError)

## Constraints
- Do not modify utils/errors.py or any file outside $ARGUMENTS.
- Do not add new AppError subclasses — use only existing ones.
- Preserve all existing function signatures.

## Verification
Run pytest -q after every function you update. All existing tests must still pass before you move to the next function. Report the final pytest output when done.