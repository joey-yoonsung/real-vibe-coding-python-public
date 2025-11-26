# Plan

> This file contains the project roadmap, milestones, and current progress.
> Claude uses this to understand project priorities and what's being worked on.

## What to Include Here

- **Roadmap**: High-level phases and goals
- **Current Focus**: What's being worked on now
- **Milestones**: Key deliverables with status
- **Backlog**: Future features and improvements

---

## Project Roadmap

### Phase 1: Foundation (Current)
- [x] Initialize project structure
- [x] Set up `.claude/` memory system
- [ ] Add basic test infrastructure
- [ ] Create sample module with TDD

### Phase 2: Core Features
- [ ] Implement main functionality
- [ ] Add comprehensive tests
- [ ] Set up CI/CD pipeline

### Phase 3: Enhancement
- [ ] Performance optimization
- [ ] Documentation
- [ ] Release preparation

---

## Current Focus

**Sprint Goal**: Set up project foundation and learn Claude Code workflows

### Active Tasks
| Task | Status | Notes |
|------|--------|-------|
| Configure `.claude/` structure | Done | Memory files created |
| Learn TDD with Claude | In Progress | Practice with simple module |

---

## Milestones

| Milestone | Target | Status |
|-----------|--------|--------|
| Project Setup | Week 1 | Done |
| First TDD Module | Week 2 | In Progress |
| CI/CD Pipeline | Week 3 | Not Started |

---

## Backlog

### High Priority
- [ ] Add pytest configuration
- [ ] Create first unit test

### Medium Priority
- [ ] Add pre-commit hooks
- [ ] Set up GitHub Actions

### Low Priority
- [ ] Add documentation site
- [ ] Performance benchmarks

---

## Example: Detailed Task Breakdown

```markdown
## Feature: User Authentication

### Tasks
1. [ ] Create User model with validation
2. [ ] Add password hashing utility
3. [ ] Implement login endpoint
4. [ ] Add JWT token generation
5. [ ] Write integration tests

### Acceptance Criteria
- Users can register with email/password
- Login returns valid JWT token
- Invalid credentials return 401
```

---

## Tips for Writing Plans

1. **Keep it updated** - Review at the start/end of each session
2. **Use checkboxes** - Easy to track progress: `- [x]` done, `- [ ]` pending
3. **Be realistic** - Don't overcommit; small achievable goals
4. **Link to tasks/** - Detailed task plans go in `.claude/tasks/` directory
5. **Review with Claude** - Ask Claude to help update plan after completing work
