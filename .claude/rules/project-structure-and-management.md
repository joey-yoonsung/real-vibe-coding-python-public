# Project Structure and Management

## Overview

This project uses [uv](https://github.com/astral-sh/uv) for Python dependency management with workspace monorepo structure.

## Project Structure

```
real-vibe-coding/
├── pyproject.toml           # Root workspace config (versions, tools)
├── uv.lock                  # Unified lockfile (committed)
├── Makefile                 # Build and test commands
├── config/
│   ├── pyproject.toml       # Module config
│   ├── src/my_config/
│   └── tests/
└── logger/
    ├── pyproject.toml
    └── src/my_logger/
```

## Workspace Member Structure

Each workspace member follows this pattern:
```
<member>/
├── pyproject.toml           # Member config with dependencies
├── src/
│   └── <package_name>/      # Importable package (my_config, my_logger, etc.)
│       ├── __init__.py
│       └── *.py
└── tests/
    ├── __init__.py
    ├── unit/                # Optional: unit tests
    └── integration/         # Optional: integration tests
```

## Key Principles

- **Root defines versions**: All library versions in `constraint-dependencies`
- **Sub-modules reference names only**: Just `"pydantic"`, not `"pydantic>=2.0.0"`
- **Shared tool config**: ruff/mypy rules in root `pyproject.toml`
- **Module-specific tests**: pytest config in each module's `pyproject.toml`
- **Build system**: Sub-modules use `uv_build`, root has `package = false`
- **Package naming**: Use `my_` prefix convention (e.g., `my_config`, `my_logger`)
- **Inter-package deps**: Use `workspace = true` in `tool.uv.sources`
