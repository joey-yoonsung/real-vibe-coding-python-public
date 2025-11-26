---
name: test-skill
description: Guide for writing and organizing tests in this project. Use when creating new tests, choosing test patterns, writing fixtures, or structuring test directories.
---

# Test Skill

## Framework
- **pytest** as the primary test framework
- Tests live in each workspace member's `tests/` directory

## Test Structure
```
<member>/tests/
├── __init__.py
├── conftest.py          # Shared fixtures for this member
├── unit/                # Fast, isolated tests
│   ├── __init__.py
│   └── test_*.py
└── integration/         # Tests with external dependencies
    ├── __init__.py
    └── test_*.py
```

## Naming Conventions
- Test files: `test_<module>.py`
- Test functions: `test_<behavior_description>`
- Use descriptive names: `test_returns_404_when_user_not_found` not `test_error`

## Test Patterns

### Basic Unit Test
```python
def test_add_returns_sum_of_two_numbers():
    result = add(2, 3)
    assert result == 5
```

### Parameterized Tests
Use `@pytest.mark.parametrize` to test multiple inputs without duplication:
```python
@pytest.mark.parametrize("a, b, expected", [
    (1, 2, 3),
    (0, 0, 0),
    (-1, 1, 0),
])
def test_add(a, b, expected):
    assert add(a, b) == expected
```

### Fixtures
Define reusable test data in `conftest.py`:
```python
@pytest.fixture
def sample_user():
    return User(name="Alice", email="alice@example.com")
```

Scope fixtures appropriately:
- `scope="function"` (default) — fresh per test
- `scope="module"` — shared within a file
- `scope="session"` — shared across all tests (use sparingly)

### FastAPI Endpoint Tests
Use `httpx.AsyncClient` or `TestClient`:
```python
from fastapi.testclient import TestClient
from my_api.main import app

client = TestClient(app)

def test_hello_returns_greeting():
    response = client.get("/hello")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World!"}
```

### Exception Testing
```python
def test_raises_value_error_on_negative_input():
    with pytest.raises(ValueError, match="must be positive"):
        process(-1)
```

## Assertion Style
- Use plain `assert` statements (pytest rewrites them for clear output)
- One logical assertion per test when possible
- For complex objects, assert specific fields rather than entire objects

## Running Tests
```bash
# All tests
uv run pytest

# Specific member
uv run --package config pytest

# Verbose with output
uv run pytest -v -s

# Run specific test
uv run pytest tests/unit/test_example.py::test_function_name

# With coverage
make ci
```

## TDD Integration
Tests are written following the Red → Green → Refactor cycle:
1. Write a failing test first
2. Implement minimum code to pass
3. Refactor if needed (tests must stay green)
