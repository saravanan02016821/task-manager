#!/usr/bin/env python3
"""PreToolUse hook for task-manager.

Blocks three kinds of things before they happen:
  1. Writes to protected files/folders (BLOCKED_PATHS), through Write/Edit/MultiEdit or Bash
  2. Dangerous shell commands (BLOCKED_COMMANDS)
  3. Hardcoded database connection strings in services/tasks.py (content guard)
"""
import json, os, re, sys


BLOCKED_PATHS = [
    "utils/errors.py",          # Do-not-touch rule 1: the AppError classes every service relies on
    "migrations/",              # Do-not-touch rule 3: no database, so nothing should ever be written here
    ".env",                     # Secrets — hard block
    ".claude/settings.json",    # Hook config — Claude shouldn't be able to turn off its own guard
]

#  Shell commands Claude must never run 
# \b = word boundary, so "rm" only matches the actual rm command (not "farm"),
# and "TABLE" doesn't match "TABLESPACE".
BLOCKED_COMMANDS = [
    (r"\b(DROP|TRUNCATE)\s+TABLE\b",
     "Destructive SQL (DROP TABLE / TRUNCATE TABLE) is not allowed."),
    (r"\brm\s+(-(?=[a-z]*r)(?=[a-z]*f)[a-z]+|-[a-z]*r[a-z]*\s+-[a-z]*f[a-z]*|-[a-z]*f[a-z]*\s+-[a-z]*r[a-z]*)\b",
     "Recursive force delete (rm -rf) is not allowed."),
    (r"\bgit\s+push\b.*\s(--force\b|-f\b)",         # my choice: force-push
     "git push --force is not allowed. It can wipe out commits on the remote."),
]

#  Content guard: allowed files that must never contain a DB connection string 
CONTENT_GUARDED_FILES = ["services/tasks.py"]
DB_URL_PATTERN = re.compile(r"postgres(ql)?://|sqlite:///", re.IGNORECASE)

# Signs that a shell command writes or changes a file 
WRITE_SIGNS = re.compile(
    r">|\btee\b|\bsed\s+-i|\bcp\b|\bmv\b|\brm\b|\btruncate\b|\btouch\b|\bmkdir\b|\bdd\b"
    r"|\bpython3?\b|\bperl\b|\bSet-Content\b|\bAdd-Content\b|\bOut-File\b|\bNew-Item\b",
    re.IGNORECASE,
)


def full_path(path: str) -> str:
    """Turn any path (short or full) into a normalized full path.

    Lowercased because Windows paths aren't case-sensitive: Utils/errors.py and
    utils/errors.py are the same file, so the check has to treat them the same.
    """
    return os.path.normpath(os.path.abspath(path)).lower()


def project_path(pattern: str) -> str:
    """Turn a path from one of the lists above into a full path inside the project."""
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
    return os.path.normpath(os.path.join(project_dir, pattern)).lower()


def is_blocked(file_path: str) -> tuple[bool, str]:
    """Return (blocked, reason) for the given file path."""
    norm = full_path(file_path)
    for pattern in BLOCKED_PATHS:
        target = project_path(pattern)
        if norm == target:
            return True, f"Protected file: {pattern}"
        if pattern.endswith("/") and norm.startswith(target):
            return True, f"Protected directory: {pattern}"
    return False, ""


def new_text(tool: str, tool_input: dict) -> str:
    """Get the text Claude is about to write, for Write, Edit, or MultiEdit."""
    if tool == "Write":
        return tool_input.get("content", "")
    if tool == "Edit":
        return tool_input.get("new_string", "")
    if tool == "MultiEdit":
        return "\n".join(e.get("new_string", "") for e in tool_input.get("edits", []))
    return ""


def bash_writes_protected_path(command: str) -> str:
    """Return the protected path a Bash command writes to, or "" if none.

    Best effort: the command has to (1) look like it writes something and
    (2) mention a protected path. Reading (cat, grep) is still allowed.
    """
    text = command.replace("\\", "/").lower()
    if not WRITE_SIGNS.search(text):
        return ""
    for pattern in BLOCKED_PATHS:
        name = pattern.lower().rstrip("/")
        if re.search(r"(?<![\w.-])" + re.escape(name) + r"(?![\w-])", text):
            return pattern
    return ""


def block(lines: list[str]) -> None:
    """Print the reason to stderr (Claude sees it) and exit 2 to block."""
    for line in lines:
        print(line, file=sys.stderr)
    sys.exit(2)


def main():
    payload = json.loads(sys.stdin.read())
    tool = payload.get("tool_name", "")
    tool_input = payload.get("tool_input", {})

    #  Branch 1: Bash commands 
    if tool == "Bash":
        command = tool_input.get("command", "")
        for pattern, reason in BLOCKED_COMMANDS:
            if re.search(pattern, command, re.IGNORECASE):
                block([f"BLOCKED: {reason}", f"Command: {command}"])

        # Path guard for Bash: stop shell writes to protected files
        protected = bash_writes_protected_path(command)
        if protected:
            block([
                f"BLOCKED: this shell command writes to a protected path: {protected}.",
                f"Command: {command}",
                "Protected files can't be changed through Bash either.",
            ])
        sys.exit(0)

    #  Branch 2: file-write tools 
    if tool in ("Write", "Edit", "MultiEdit"):
        file_path = tool_input.get("file_path") or tool_input.get("path", "")

        blocked, reason = is_blocked(file_path)
        if blocked:
            block([
                f"BLOCKED: {reason}. This file is protected by project policy.",
                f"To modify {file_path}, update CLAUDE.md and remove the",
                "protection after team review.",
            ])

        # Content guard
        norm = full_path(file_path)
        for guarded in CONTENT_GUARDED_FILES:
            if norm == project_path(guarded) and DB_URL_PATTERN.search(new_text(tool, tool_input)):
                block([
                    f"BLOCKED: hardcoded database connection string in {guarded}.",
                    "Connection strings (postgresql://, sqlite:///) must come from environment",
                    "variables, e.g. os.environ['DATABASE_URL'], never be written into the code.",
                ])

    sys.exit(0)


if __name__ == "__main__":
    main()
