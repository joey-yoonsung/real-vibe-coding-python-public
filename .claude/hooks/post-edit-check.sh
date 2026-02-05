#!/bin/bash
# Post-edit hook: runs ruff format, ruff lint (with isort), and mypy on edited Python files.
# Based on .pre-commit-config.yaml configuration.

set -euo pipefail

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

# Skip if no file path or not a Python file
if [[ -z "$FILE_PATH" || "$FILE_PATH" != *.py ]]; then
  exit 0
fi

# Skip files in excluded directories (matching pre-commit exclusions)
if [[ "$FILE_PATH" =~ ^\.pre-commit-scripts/ || "$FILE_PATH" =~ ^\.claude/ ]]; then
  exit 0
fi

cd "$CLAUDE_PROJECT_DIR"

# 0. Ensure dependencies are synced
uv sync --all-packages --all-groups --locked -q 2>/dev/null || true

ERRORS=""

# 1. Ruff format (Black-style formatter)
if ! uv run ruff format "$FILE_PATH" 2>/dev/null; then
  ERRORS+="ruff format failed on $FILE_PATH\n"
fi

# 2. Ruff isort (import sorting)
if ! uv run ruff check --select=I --fix "$FILE_PATH" 2>/dev/null; then
  ERRORS+="ruff isort failed on $FILE_PATH\n"
fi

# 3. Ruff lint (static analysis) - no auto-fix, report only
LINT_OUTPUT=$(uv run ruff check "$FILE_PATH" 2>&1) || true
if [[ -n "$LINT_OUTPUT" ]]; then
  ERRORS+="ruff lint issues in $FILE_PATH:\n$LINT_OUTPUT\n"
fi

# 4. mypy (type checking) - skip test files matching pre-commit exclusion
if [[ ! "$FILE_PATH" =~ ^tests/ ]]; then
  MYPY_OUTPUT=$(uv run mypy "$FILE_PATH" 2>&1) || true
  if echo "$MYPY_OUTPUT" | grep -q "error:"; then
    ERRORS+="mypy errors in $FILE_PATH:\n$MYPY_OUTPUT\n"
  fi
fi

# Report results
if [[ -n "$ERRORS" ]]; then
  echo -e "$ERRORS" >&2
  exit 2
fi

exit 0
