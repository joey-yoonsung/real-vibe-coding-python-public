---
name: plan-skill
description: Guide for writing task plans and implementation plans. Use when starting a new task, creating a plan file, or updating plan progress.
---

# Plan Skill

## When to Write a Plan
- Before starting any new task or feature
- When the scope involves more than a trivial change
- When requirements need to be broken into steps

## Plan File Location
- **Task plans**: `.claude/tasks/<task-name>.md` (git-ignored, local only)
- **Project plan**: `.claude/plan.md` (committed, project-level roadmap)

## Task Plan Template

```markdown
# Task: <Title>

## Summary
<1-2 sentence description of what this task accomplishes>

## Context
<Why this task is needed, relevant background>

## Implementation Plan

### Step 1: <Structural/Behavioral> — <Description>
- <Detail>
- <Detail>

### Step 2: <Structural/Behavioral> — <Description>
- <Detail>

## Acceptance Criteria
- [ ] <Criterion 1>
- [ ] <Criterion 2>
- [ ] All tests pass (`uv run pytest`)
- [ ] Code quality checks pass (`uv run pre-commit run`)

## Status
- [ ] Step 1
- [ ] Step 2
```

## Plan Writing Rules

1. **Label each step** as Structural or Behavioral (Tidy First principle)
2. **Structural changes first** — reorganize code before adding behavior
3. **Small steps** — each step should be independently verifiable
4. **Include verification** — how to confirm each step succeeded
5. **Get human review** — always confirm plan with human before implementation

## Updating Plans
- Mark steps as complete: `- [x] Step 1`
- Add notes on deviations or discoveries
- If scope changes significantly, update the plan and re-confirm with human

## Project Plan (`plan.md`)
The project-level plan tracks milestones and phases. Update when:
- Major milestones are completed
- Project direction changes
- New phases begin
