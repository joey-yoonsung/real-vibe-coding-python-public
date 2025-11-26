# Conventions

> This file defines coding standards, naming rules, and patterns.
> Claude uses this to write code that matches your team's style.

## What to Include Here

- **Code Style**: Formatting, indentation, line length
- **Naming Conventions**: Variables, functions, classes, files
- **Design Patterns**: Preferred architectural patterns
- **Anti-patterns**: What to avoid

---

## Code Style

### Formatting
- **Indentation**: 4 spaces (Python standard)
- **Line length**: 88 characters max (ruff default)
- **Quotes**: Double quotes for strings
- **Trailing commas**: Always in multi-line structures

### Example
```python
# Good
def calculate_total(
    items: list[Item],
    discount: float = 0.0,
) -> float:
    """Calculate total price with optional discount."""
    subtotal = sum(item.price for item in items)
    return subtotal * (1 - discount)

# Bad - avoid single letter variables, missing type hints
def calc(i, d):
    return sum(x.price for x in i) * (1 - d)
```

---

## Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Variables | snake_case | `user_count`, `is_active` |
| Functions | snake_case | `get_user()`, `calculate_total()` |
| Classes | PascalCase | `UserService`, `OrderItem` |
| Constants | UPPER_SNAKE | `MAX_RETRIES`, `API_TIMEOUT` |
| Files | snake_case | `user_service.py`, `test_orders.py` |
| Test functions | test_*_should_* | `test_user_should_have_email()` |

---

## Design Patterns

### Dependency Injection (Required)
```python
# Good - dependencies are injected
class UserService:
    def __init__(self, repository: UserRepository, logger: Logger):
        self.repository = repository
        self.logger = logger

# Bad - dependencies created internally
class UserService:
    def __init__(self):
        self.repository = UserRepository()  # Hard to test!
        self.logger = Logger()
```

### Composition Over Inheritance
```python
# Good - composition
class EmailNotifier:
    def __init__(self, sender: EmailSender):
        self.sender = sender

# Avoid - deep inheritance hierarchies
class EmailNotifier(Notifier, Sender, Logger):  # Too complex
    pass
```

---

## File Organization

### Simple Project
```
src/
├── module_name/
│   ├── __init__.py
│   ├── models.py       # Data classes, Pydantic models
│   ├── service.py      # Business logic
│   ├── repository.py   # Data access
│   └── exceptions.py   # Custom exceptions
tests/
├── unit/
│   └── test_service.py
└── integration/
    └── test_api.py
```

### Complex Project (Multiple Packages)
```
src/
├── module_name/
│   ├── __init__.py
│   │
│   ├── core/                  # Core business logic
│   │   ├── __init__.py
│   │   ├── entities.py        # Domain entities
│   │   ├── use_cases.py       # Application use cases
│   │   └── interfaces.py      # Abstract interfaces (ports)
│   │
│   ├── infrastructure/        # External integrations
│   │   ├── __init__.py
│   │   ├── database/
│   │   │   ├── __init__.py
│   │   │   ├── repository.py  # DB repository implementation
│   │   │   └── models.py      # ORM models
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py      # API endpoints
│   │   │   └── schemas.py     # Request/Response schemas
│   │   └── external/
│   │       ├── __init__.py
│   │       └── client.py      # External API clients
│   │
│   ├── config/                # Configuration
│   │   ├── __init__.py
│   │   └── settings.py        # App settings
│   │
│   └── utils/                 # Shared utilities
│       ├── __init__.py
│       └── helpers.py
│
tests/
├── unit/
│   ├── core/
│   │   └── test_use_cases.py
│   └── infrastructure/
│       └── test_repository.py
├── integration/
│   └── test_api.py
└── conftest.py                # Shared fixtures
```

**Rules**:
- One class per file for main domain classes
- Package names are plural or descriptive (`infrastructure/`, `utils/`)
- Test structure mirrors source structure

---

## Anti-patterns to Avoid

1. **God classes** - Classes doing too many things
2. **Magic numbers** - Use named constants instead
3. **Mutable default arguments** - Use `None` and check inside function
4. **Bare except** - Always specify exception type
5. **Print debugging** - Use proper logging

```python
# Bad - mutable default
def add_item(item, items=[]):  # Bug! List is shared
    items.append(item)

# Good
def add_item(item, items: list | None = None):
    if items is None:
        items = []
    items.append(item)
```

---

## Tips for Writing Conventions

1. **Be specific** - "Use 4 spaces" not "indent properly"
2. **Show examples** - Good and bad code side by side
3. **Explain why** - Helps developers understand the reasoning
4. **Keep it short** - Only include what's frequently needed
