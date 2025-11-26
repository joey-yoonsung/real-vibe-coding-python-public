# Task: Update Claude Settings Based on Practical Guide

## Summary
Reflect the recommendations from `Practical-Coding-Agent-and-Repository-Setup-Claude_260205.md` into the repository's `.claude/` configuration.
CLAUDE.md content is agent behavior guide, not TDD-specific — keep as-is.

## Implementation Plan

### Step 1: Add `dev.md` rule
- Dev environment activation (uv sync, venv)
- Post-development verification commands
- Pre-commit integration as mandatory step

### Step 2: Update `python-coding-convention.md`
- Add explicit "Run this for every task" enforcement directive
- Reference integrated pre-commit command

### Step 3: Add `/clarify` command
- Create `.claude/commands/clarify.md`
- For clarifying unclear requirements during design/plan phases

### Step 4: Add missing skills
- test-skill: pytest patterns, parameterized, fixtures, integration tests
- pyproject-toml-skill: uv workspace build file management
- plan-skill: plan writing methodology and templates

### Step 5: Update CLAUDE.md (minimal)
- Add reference to `/clarify` for unclear requirements

## Status
- [ ] Step 1
- [ ] Step 2
- [ ] Step 3
- [ ] Step 4
- [ ] Step 5
