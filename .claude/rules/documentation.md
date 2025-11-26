# Documentation Guidelines

## When to Write Each Document Type

### plan.md (.claude/plan.md)

**Purpose**: Overall project plan and milestones

**When to update**:
- At project inception to define roadmap
- When major milestones are completed
- When project direction changes significantly
- During sprint/iteration planning

**Contents**:
- Project goals and objectives
- Milestones with completion criteria
- High-level timeline (phases, not dates)
- Dependencies between components

### Task Plans (.claude/tasks/)

**Purpose**: Temporal memory for current work

**When to create**:
- When starting any new task or feature
- Before beginning implementation work
- When requirements need clarification

**Rules**:
- Files in tasks/ are Git-ignored (local only)
- Use `current-task.md` for active work
- Archive completed tasks if needed for reference

### ADR (Architecture Decision Records)

**Purpose**: Document significant architectural decisions

**Location**: `docs/adr/`

**When to write**:
- Choosing between multiple viable solutions
- Adopting new frameworks or libraries
- Changing existing architecture patterns
- Making trade-offs that affect the system long-term

**When to update**:
- Decision status changes (Proposed → Accepted)
- Decision is deprecated or superseded by a new ADR
- Never modify the core decision content; create a new ADR instead

**How to write**: Use the `adr-skill` for template, format, and best practices.

### CLAUDE.md (.claude/CLAUDE.md)

**Purpose**: Main project context for Claude Code

**When to update**:
- Project setup or significant restructuring
- Adding new development commands
- Changing core development workflow
- Updating project-wide conventions

**Keep it minimal**:
- Project overview (1-2 sentences)
- Essential development commands
- Links to detailed documentation
- Language requirements

### README.md (Project Root)

**Purpose**: Human-readable project introduction

**When to write/update**:
- Project creation
- Adding new features users need to know about
- Changing installation or usage instructions
- Release announcements

**Contents**:
- Project description and purpose
- Installation instructions
- Usage examples
- Contributing guidelines
- License information

### README.md (Sub-modules)

**Purpose**: Module-specific documentation

**When to write**:
- Creating new packages/modules
- Module has unique setup requirements
- Complex modules needing explanation

**Contents**:
- Module purpose and responsibility
- API documentation
- Usage examples specific to the module
- Dependencies

## Documentation Hierarchy

```
project-root/
├── README.md                    # Project intro for humans
├── docs/
│   ├── adr/                     # Architecture decisions
│   │   └── 001-database-choice.md
│   └── api/                     # API documentation
│
├── .claude/
│   ├── CLAUDE.md                # Claude context (minimal)
│   ├── plan.md                  # Project roadmap
│   ├── techspec.md              # Technical specifications
│   └── tasks/                   # Current work
│
└── src/
    └── module/
        └── README.md            # Module-specific docs
```

## Best Practices

1. **Keep documentation close to code** - README.md in each module
2. **Update docs with code changes** - Part of the PR process
3. **Use examples liberally** - Code examples are clearer than descriptions
4. **Link, don't duplicate** - Reference other docs instead of copying
5. **Review periodically** - Outdated docs are worse than no docs
