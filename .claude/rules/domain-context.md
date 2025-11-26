# Context

> This file contains project background, domain knowledge, and business context.
> Claude uses this to understand "why" the project exists and "what" problem it solves.

## What to Include Here

- **Project Purpose**: Why does this project exist?
- **Target Users**: Who will use this?
- **Domain Knowledge**: Industry-specific terms or concepts
- **Business Rules**: Important constraints or requirements
- **External Dependencies**: Third-party services or APIs

---

## Project Overview

This is a practice project for learning Claude Code workflows and best practices.

### Purpose
- Learn how to structure Claude Code projects effectively
- Practice TDD (Test-Driven Development) with Claude assistance
- Understand `.claude/` directory organization

### Target Users
- Developers learning Claude Code
- Teams adopting AI-assisted development

---

## Example: Domain Knowledge Section

```markdown
## Domain Terms

| Term | Definition |
|------|------------|
| TDD | Test-Driven Development - write tests before code |
| Skill | Reusable Claude instruction set for specific tasks |
| Memory | Persistent context Claude reads at session start |
```

## Example: Business Rules Section

```markdown
## Business Rules

- All code must have >80% test coverage before merge
- API responses must complete within 500ms
- User data must be encrypted at rest
```

---

## Tips for Writing Context

1. **Be specific** - Include actual numbers, names, and constraints
2. **Update regularly** - Context changes as the project evolves
3. **Avoid duplication** - Don't repeat what's in other files
4. **Think "onboarding"** - What would a new developer need to know?
