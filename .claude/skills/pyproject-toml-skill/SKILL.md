---
name: pyproject-toml-skill
description: Guide for managing pyproject.toml files in this uv workspace monorepo. Use when adding dependencies, creating new workspace members, or modifying build configuration.
---

# pyproject.toml Skill

## Workspace Architecture

This project uses **uv workspace** monorepo structure.

### Root `pyproject.toml`
- `package = false` — root is not a package itself
- Defines `tool.uv.workspace.members` listing all sub-modules
- `constraint-dependencies` — single source of truth for all library versions
- Shared tool config: ruff, mypy rules

### Member `pyproject.toml`
- Each member is a buildable package using `uv_build`
- Dependencies reference **names only** (no versions) — versions come from root constraints
- Member-specific pytest config in `[tool.pytest.ini_options]`

## Key Principles

1. **Root defines versions**: All library versions in `constraint-dependencies`
2. **Sub-modules reference names only**: Just `"pydantic"`, not `"pydantic>=2.0.0"`
3. **Inter-package deps**: Use `workspace = true` in `[tool.uv.sources]`
4. **Package naming**: Use `my_` prefix (e.g., `my_config`, `my_logger`, `my_api`)

## Creating a New Workspace Member

### 1. Create directory structure
```
<member>/
├── pyproject.toml
├── src/
│   └── my_<member>/
│       └── __init__.py
└── tests/
    └── __init__.py
```

### 2. Member pyproject.toml template
```toml
[project]
name = "my-<member>"
version = "0.0.1"
requires-python = ">=3.12"
dependencies = []

[dependency-groups]
dev = []

[build-system]
requires = ["hatchling", "uv_build"]
build-backend = "hatchling.build"

[tool.hatch.build.hooks.uv_build]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
```

### 3. Register in root pyproject.toml
- Add to `tool.uv.workspace.members`
- Add first-party package to `tool.ruff.lint.isort.known-first-party`

### 4. Update Makefile
- Add test target for the new member
- Add to `test-all` dependency list

## Adding Dependencies

### External dependency
```bash
# Add to specific member
uv add --package <member> <library>

# Version is controlled by root constraint-dependencies
```

### Inter-workspace dependency
In member's `pyproject.toml`:
```toml
[project]
dependencies = ["my-config"]

[tool.uv.sources]
my-config = { workspace = true }
```

## Common Operations
```bash
uv sync --all-packages --all-groups --locked -v  # Sync all
uv lock --upgrade                                 # Update lockfile
uv add --package config pydantic-settings         # Add dep
uv build --package config                         # Build package
```
