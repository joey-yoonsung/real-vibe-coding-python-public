---
name: adr-skill
description: "Guide for writing Architecture Decision Records (ADR). Use when documenting architectural decisions, recording technology choices, or creating technical decision logs. This skill defines the ADR structure, format, and best practices."
---

# Architecture Decision Records (ADR)

ADR is a short text file that documents crucial architectural decisions in software projects.

## Purpose

| Purpose | Description |
|---------|-------------|
| **Knowledge Preservation** | Record "why" specific technical selections were made |
| **Onboarding** | New members quickly grasp project's technical history |
| **Avoiding Repetition** | Prevent revisiting settled discussions |
| **Accountability** | Transparent records of who decided what and when |

ADRs solve "architecture amnesia" by preventing loss of institutional knowledge.

## File Location and Naming

```
docs/adr/
├── ADR-001-database-selection.md
├── ADR-002-authentication-method.md
├── ADR-003-api-versioning-strategy.md
└── ...
```

**Naming Convention**: `ADR-{NUMBER}-{kebab-case-title}.md`

## ADR Structure

### Template

```markdown
# ADR-{NUMBER}: {Title}

## Status

{Proposed | Accepted | Deprecated | Superseded by ADR-XXX}

## Date

{YYYY-MM-DD}

## Context

{Background information and constraints driving the decision.
What is the issue that we're seeing that is motivating this decision?}

## Decision

{The chosen approach, clearly stated.
What is the change that we're proposing and/or doing?}

## Rationale

{Explanation of why this option was selected.
Why did we choose this over other alternatives?}

## Alternatives Considered

### {Alternative 1}
- Pros: ...
- Cons: ...
- Why rejected: ...

### {Alternative 2}
- Pros: ...
- Cons: ...
- Why rejected: ...

## Consequences

{System impacts and implementation implications.
What becomes easier or more difficult because of this change?}

### Positive
- ...

### Negative
- ...

### Risks
- ...
```

## Example

```markdown
# ADR-001: Use PostgreSQL for Primary Database

## Status

Accepted

## Date

2024-03-15

## Context

We need to select a primary database for our new microservice.
The service requires ACID compliance, complex queries with joins,
and needs to handle approximately 10,000 transactions per second.

## Decision

We will use PostgreSQL as our primary database.

## Rationale

PostgreSQL provides robust ACID compliance, excellent performance
for complex queries, and has strong community support. Our team
has existing expertise with PostgreSQL.

## Alternatives Considered

### MySQL
- Pros: Widely adopted, good performance
- Cons: Less robust for complex queries
- Why rejected: PostgreSQL's advanced features better fit our needs

### MongoDB
- Pros: Flexible schema, horizontal scaling
- Cons: No ACID for multi-document transactions (at decision time)
- Why rejected: ACID compliance is a hard requirement

## Consequences

### Positive
- Strong data integrity guarantees
- Rich query capabilities
- Familiar technology for the team

### Negative
- Vertical scaling limitations
- Requires careful schema design upfront

### Risks
- May need sharding strategy for future growth
```

## Status Lifecycle

```
Proposed → Accepted → [Deprecated | Superseded by ADR-XXX]
```

| Status | Description |
|--------|-------------|
| **Proposed** | Under discussion, not yet finalized |
| **Accepted** | Decision made and in effect |
| **Deprecated** | No longer relevant or applicable |
| **Superseded** | Replaced by a newer ADR |

## Best Practices

1. **Record the "Why"**: Focus on rationale, not just what was chosen
2. **Document alternatives**: Include options considered and why rejected
3. **One decision per ADR**: Keep each record focused on a single decision
4. **Version control**: Store ADRs in Git alongside code
5. **Keep immutable**: Don't modify accepted ADRs; create new ones to supersede
6. **Update status**: Mark as deprecated/superseded when decisions change
7. **Link related ADRs**: Reference related decisions when applicable

## When to Write an ADR

Write an ADR when:
- Choosing between multiple viable technical solutions
- Adopting new frameworks or libraries
- Changing existing architecture patterns
- Making trade-offs that affect the system long-term
- Decisions that future team members might question

## References

- https://www.cncf.co.kr/blog/adr-guide/
- https://www.cncf.co.kr/blog/adr-architecture-decision-record/
