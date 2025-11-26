# Tech Spec

> This file contains technical specifications, tools, and development environment setup.
> Claude uses this to understand what technologies to use and how to run commands.

## What to Include Here

- **Tech Stack**: Languages, frameworks, versions
- **Development Tools**: Linters, formatters, testing tools
- **Commands**: Build, test, lint, deploy commands
- **Environment**: Required environment variables, dependencies

---

## Tech Stack

| Category | Technology | Version |
|----------|------------|---------|
| Language | Python | 3.12+ |
| Package Manager | uv | latest |
| Testing | pytest | latest |
| Linting | ruff | latest |
| Type Checking | mypy | latest |
| Git Hooks | pre-commit | latest |

---

## Development Commands

### Setup
```bash
# Install dependencies
uv sync --all-packages --all-groups -v

# Install pre-commit hooks
uv run pre-commit install
```

### Daily Development
```bash
# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src --cov-report=term-missing

# Run specific test file
uv run pytest tests/test_example.py -v

# Run linting and formatting
uv run pre-commit run --all-files

# Run only ruff (linting)
uv run ruff check .

# Run only ruff (formatting)
uv run ruff format .

# Run type checking
uv run mypy src/
```

### Quick Reference
| Action | Command |
|--------|---------|
| Install deps | `uv sync --all-packages --all-groups -v` |
| Run tests | `uv run pytest` |
| Lint all | `uv run pre-commit run` |
| Format code | `uv run ruff format .` |
| Type check | `uv run mypy src/` |

---

## Project Structure

```
project-root/
├── .claude/              # Claude Code memory files
├── src/                  # Source code
│   └── package_name/
├── tests/                # Test files
│   ├── unit/
│   └── integration/
├── pyproject.toml        # Project configuration
├── uv.lock               # Dependency lock file
└── README.md
```

---

## Tool Configuration

### pyproject.toml Example
```toml
[project]
name = "your-project"
version = "0.1.0"
requires-python = ">=3.12"

[tool.ruff]
line-length = 88
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP"]

[tool.mypy]
python_version = "3.12"
strict = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
```

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ENV` | Environment (dev/staging/prod) | `dev` |
| `LOG_LEVEL` | Logging verbosity | `INFO` |
| `DEBUG` | Enable debug mode | `false` |

### Local Setup (.env)
```bash
# .env.example
ENV=dev
LOG_LEVEL=DEBUG
DEBUG=true
```

---

## Example: Adding a New Dependency

```bash
# Add production dependency
uv add package-name

# Add development dependency
uv add --dev package-name

# Update lock file
uv lock
```

---

## Tips for Writing Tech Specs

1. **Keep commands copy-pasteable** - Users should be able to copy and run directly
2. **Include versions** - Helps avoid compatibility issues
3. **Document quirks** - Any non-obvious setup steps or workarounds
4. **Update with project** - Add new tools as they're introduced
