---
paths: "**/*.py"
---

# Python Coding Conventions

## Code Style

All code must pass the pre-commit hooks defined in `.pre-commit-config.yaml`:

- **ruff-format**: Black-style code formatting
- **ruff (isort)**: Import sorting
- **ruff (lint)**: Static analysis (see `pyproject.toml` for rule selection)
- **mypy**: Static type checking (strict mode)
- **typos**: Spell checking
- **bandit**: Security scanning

The following script forces to meet coding conventions and styles. Run this for every task.
```bash
uv run pre-commit run
```

## Design Patterns
### Good Pattterns 
- Dependency Injection (Required)
- Composition Over Inheritance
- SOLID pricnciples

### Anti-patterns to Avoid
1. **God classes** - Classes doing too many things
2. **Magic numbers** - Use named constants instead
3. **Mutable default arguments** - Use `None` and check inside function
4. **Bare except** - Always specify exception type
5. **Print debugging** - Use logger

## Project Specific Guide

### Logging
Use my-logger instead of print or standard logger.
