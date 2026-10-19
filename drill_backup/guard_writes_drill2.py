#!/usr/bin/env python3
"""PreToolUse hook: blocks writes to protected files and directories."""
import json, sys, os

# ── Paths this project must never let Claude write to ──────────────
# Populated from my CLAUDE.md Do-not-touch section.
BLOCKED_PATHS = [
    "utils/errors.py",          # Do-not-touch rule 1: the AppError classes every service relies on
    "migrations/",              # Do-not-touch rule 3: no database, so nothing should ever be written here
    ".env",                     # Secrets — hard block
    ".claude/settings.json",    # Hook config — Claude shouldn't be able to turn off its own guard
]


def is_blocked(file_path: str) -> tuple[bool, str]:
    """Return (blocked, reason) for the given file path."""
    # Claude Code sends full paths (C:\...\task-manager\utils\errors.py), so turn
    # both the incoming path and each BLOCKED_PATHS entry into full paths first.
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
    norm = os.path.normpath(os.path.abspath(file_path))
    for pattern in BLOCKED_PATHS:
        target = os.path.normpath(os.path.join(project_dir, pattern))
        if norm == target:
            return True, f"Protected file: {pattern}"
        if pattern.endswith("/") and norm.startswith(target):
            return True, f"Protected directory: {pattern}"
    return False, ""


def main():
    payload = json.loads(sys.stdin.read())
    tool = payload.get("tool_name", "")

    # Only inspect file-write tools
    if tool not in ("Write", "Edit", "MultiEdit"):
        sys.exit(0)

    file_path = (
        payload.get("tool_input", {}).get("file_path")
        or payload.get("tool_input", {}).get("path", "")
    )

    blocked, reason = is_blocked(file_path)
    if blocked:
        print(f"BLOCKED: {reason}. This file is protected by project policy.", file=sys.stderr)
        print(f"To modify {file_path}, update CLAUDE.md and remove the", file=sys.stderr)
        print("protection after team review.", file=sys.stderr)
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()