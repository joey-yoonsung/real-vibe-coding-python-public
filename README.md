# Real Vibe Coding

A practice project for learning Claude Code usage with Python monorepo structure with uv.

## Prerequisites

### Install uv

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Homebrew:**
```bash
brew install uv
```

Verify installation:
```bash
uv --version
```

## Setup

Clone the repository and install dependencies:

```bash
git clone <repository-url>
cd real-vibe-coding

# Install all dependencies (automatically creates .venv if needed)
uv sync --all-packages --all-groups --locked -v
```

> **Note:** `uv sync` automatically creates a `.venv` directory if one doesn't exist.
> To use a specific Python version, create the venv first:
> ```bash
> uv venv --python 3.12
> uv sync --all-packages --all-groups --locked -v
> ```

## Project Structure

```
real-vibe-coding/
├── config/          # Shared configuration module
├── logger/          # Structured logging module
├── pyproject.toml   # Root workspace configuration
├── uv.lock          # Locked dependencies
└── Makefile         # Build and test commands
```

## Development

### Running Tests

```bash
# Run all tests
uv run pytest

# Run tests for specific module
make test-config
make test-logger
```

### Code Quality

```bash
# Run linter and formatter
uv run pre-commit run

# Full CI check (tests + coverage)
make ci
```

### Adding Dependencies

```bash
# Add to specific package
uv add --package config pydantic

# Update lock file
uv lock --upgrade
```

## License

MIT
