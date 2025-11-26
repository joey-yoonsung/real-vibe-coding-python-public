# Development Environment

## Environment Activation
Every agent session must start with dependency sync:
```bash
uv sync --all-packages --all-groups --locked -v
```

## Post-Development Verification
The following scripts force to meet coding conventions and styles. Run this for every task.
```bash
uv run pre-commit run
```

After verification passes, run the full test suite:
```bash
uv run pytest
```

For comprehensive CI validation (tests + coverage):
```bash
make ci
```

## Update depenency
When add new depenency or change existing, Run this.
```
uv sync --all-packages --all-groups -v
```

## Dev Server
