---
name: config-skill
description: "Guide for creating and managing configuration classes in this project. Use when creating new config classes, loading configuration from environment variables, implementing domain-specific configs (Redis, OpenAI, S3, etc.), integrating with FastAPI or LangGraph, or working with sensitive field masking. This skill defines the two-type config system: Settings (BaseSettings) for app-level config and ConfigBase (BaseModel) for domain configs."
---

# Configuration Class System

Two-type configuration architecture: **Settings** for app-level config and **ConfigBase** for domain configs.

## Type Selection

| Use Case | Class | Base |
|----------|-------|------|
| App-level settings (workers, ports, timeouts) | Settings | `BaseSettings` |
| Domain configs (Redis, OpenAI, S3, LLM) | YourConfig | `ConfigBase` |
| FastAPI request/response models | YourConfig | `ConfigBase` |
| LangGraph state classes | YourConfig | `ConfigBase` |

## ConfigBase Usage

Import from `my_config`:

```python
from my_config import ConfigBase
```

### Basic Domain Config

```python
class RedisConfig(ConfigBase):
    host: str = "localhost"
    port: int = 6379
    password: str | None = None
    db: int = 0

    def get_url(self) -> str:
        if self.password:
            return f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"
        return f"redis://{self.host}:{self.port}/{self.db}"
```

### Loading from Environment

Use `from_env()` for explicit environment loading:

```python
# Environment: REDIS_HOST=prod-redis, REDIS_PORT=6380, REDIS_PASSWORD=secret
config = RedisConfig.from_env(prefix="REDIS_")
```

### Nested Model Support

Double separator (`__`) for nested fields, up to 3 levels deep:

```python
class PoolConfig(BaseModel):
    max_size: int = 10
    timeout: float = 30.0

class DatabaseConfig(ConfigBase):
    host: str
    port: int = 5432
    pool: PoolConfig = PoolConfig()

# Environment:
# DB_HOST=db.example.com
# DB_POOL__MAX_SIZE=50
# DB_POOL__TIMEOUT=60.5
config = DatabaseConfig.from_env(prefix="DB_")
```

### Sensitive Field Masking

Auto-masked by postfix: `*password`, `*pw`, `*key`, `*secret`, `*credentials`

```python
config = RedisConfig(host="localhost", password="secret123")
print(config.get_printable_config())
# {'host': 'localhost', 'port': 6379, 'password': 'se...23', 'db': 0}
```

### Extra Fields (kwargs)

ConfigBase allows extra fields via `extra="allow"`:

```python
config = RedisConfig(host="localhost", custom_option="value")
print(config.get_extra_configs())  # {"custom_option": "value"}
```

## Settings Integration

Settings uses `@cached_property` with `ConfigBase.from_env()`:

```python
from functools import cached_property
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )

    # App-level settings only
    worker_slots: int = Field(default=5)
    server_port: int = Field(default=8080)

    @cached_property
    def redis_config(self) -> RedisConfig:
        return RedisConfig.from_env(prefix="REDIS_")

    @cached_property
    def openai_config(self) -> OpenAIConfig:
        return OpenAIConfig.from_env(prefix="OPENAI_")
```

Access: `settings.redis_config.host`, `settings.openai_config.api_key`

## FastAPI Integration

ConfigBase classes work directly as request/response models:

```python
from fastapi import FastAPI, Depends

app = FastAPI()

@app.post("/llm/run")
async def run_llm(
    request: LLMProviderConfig,  # From request body
    settings: Settings = Depends(get_settings)  # From env
):
    redis_url = settings.redis_config.get_url()
    return {"status": "ok"}
```

## Testing

Direct instantiation without env dependencies:

```python
def test_redis_config():
    config = RedisConfig(host="test-redis", port=6380)
    assert config.get_url() == "redis://test-redis:6380/0"

def test_printable_masks_password():
    config = RedisConfig(password="secret123")
    printable = config.get_printable_config()
    assert printable["password"] == "se...23"
```

## from_env() Reference

```python
ConfigClass.from_env(
    prefix: str = "",       # e.g., "REDIS_"
    separator: str = "_",   # Field separator
    max_depth: int = 3,     # Max nesting depth
    **defaults: Any         # Fallback values
)
```

Type coercion: `bool` (true/1/yes/on), `int`, `float`, `list` (comma-separated)

## Key Principles

1. **No field duplication**: Define fields once in ConfigBase, not in Settings
2. **Explicit loading**: `from_env()` makes env loading clear and intentional
3. **Single source of truth**: Domain config fields live in ConfigBase classes
4. **Testing friendly**: Direct instantiation works without environment setup
5. **FastAPI compatible**: All ConfigBase classes work as request bodies
