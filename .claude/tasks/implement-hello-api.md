# Task: Implement Hello World API

## Goal
Create a new `api` workspace member with a FastAPI Hello World endpoint.

## Plan

### 1. Structural: Create api workspace member
- Create `api/pyproject.toml` with fastapi + uvicorn dependencies
- Create `api/src/my_api/__init__.py`
- Create `api/src/my_api/app.py` with FastAPI app
- Create `api/tests/__init__.py`
- Add `"api"` to root `pyproject.toml` workspace members
- Add `"api"` to Makefile MEMBERS

### 2. Behavioral: Implement Hello World (TDD)
- **Red**: Write test for `GET /hello` returning `{"message": "Hello, World!"}`
- **Green**: Implement the endpoint in `app.py`
- **Refactor**: If needed

### 3. Verify
- Run `uv sync --all-packages --all-groups --locked -v` (will need `uv lock` first since we added a member)
- Run `uv run pytest`
- Run `uv run pre-commit run`
- Run `make ci`

## Endpoint Spec
- `GET /hello` -> `{"message": "Hello, World!"}`
