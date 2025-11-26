---
paths: ".claude/skills/**/*"
---

# Claude Skills Management

## When to Create Skills

- Always review sustainability at the end of design or code improvement work
- After various experiments and discussions, review sustainability once a new design pattern or interface structure is established
- If deemed sustainable, consider saving that functionality as a single Claude skill within Claude Skills
- At the end of the task, suggest saving it as a Claude skill

## Skill Structure

Each skill should be organized as follows:

```
.claude/skills/
└── <skill-name>/
    ├── SKILL.md             # Skill definition and instructions (required)
    ├── references/          # Optional: reference documents
    │   └── *.md
    └── scripts/             # Optional: helper scripts
        └── *.py
```

## Creating New Skills

If the user decides to save it as a Claude skill, use the `skill-creator` skill to create the new skill.
