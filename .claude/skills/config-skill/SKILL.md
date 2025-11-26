---
name: config-skill
description: "Guide for creating and managing configuration classes in this project. Use when creating new config classes, loading configuration from environment variables, implementing domain-specific configs (Redis, OpenAI, S3, etc.), integrating with FastAPI or LangGraph, or working with sensitive field masking. This skill defines the two-type config system: Settings (SettingsBase) for app-level config and ConfigBase (BaseModel) for domain configs."
---

# Configuration Class System

Two-type configuration architecture with inheritance-based deduplication:
- **Settings** (inherits from SettingsBase) for app-level config
- **ConfigBase** (inherits from BaseModel) for domain configs
- **SettingsBase** provides shared `model_config` and `_load_config()` helper

## Type Selection

| Use Case | Class | Base |
|----------|-------|------|
| App-level settings (workers, ports, timeouts) | Settings | `SettingsBase` |
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

Use `from_env()` for explicit environment loading with multiple sources:

**Precedence order** (highest to lowest):
1. `os.environ` (runtime environment variables)
2. `.env` file (if `env_file` parameter provided)
3. Class defaults or `**defaults` parameter

```python
# From os.environ only
config = RedisConfig.from_env(prefix="REDIS_")

# From .env file (with os.environ taking precedence)
config = RedisConfig.from_env(prefix="REDIS_", env_file=".env")

# Custom .env file path
config = RedisConfig.from_env(prefix="REDIS_", env_file="/path/to/custom.env")
```

**Example .env file:**
```bash
REDIS_HOST=prod-redis
REDIS_PORT=6380
REDIS_PASSWORD=secret
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

## SettingsBase: Eliminating Duplication

**Problem**: Every Settings class duplicated `model_config` and `_load_config()` helper.

**Solution**: SettingsBase provides both via inheritance.

```python
from air_common import SettingsBase
from functools import cached_property

class Settings(SettingsBase):  # Inherits model_config and _load_config()
    # NO model_config needed - inherited from SettingsBase!
    # Provides: env_file=".env", case_sensitive=False, extra="ignore", utf-8

    # App-level settings only
    worker_slots: int = 5
    server_port: int = 8080

    # Clean one-liners using inherited _load_config()
    @cached_property
    def redis_config(self) -> RedisConfig:
        return self._load_config(RedisConfig, prefix="REDIS_")

    @cached_property
    def openai_config(self) -> OpenAIConfig:
        return self._load_config(OpenAIConfig, prefix="OPENAI_")
```

**Benefits**:
- ✅ No `model_config` duplication across services
- ✅ No `_load_config()` duplication across services
- ✅ Consistent defaults across all Settings classes
- ✅ Can override `model_config` if needed (flexible)
- ✅ Type-safe helper with proper generics

Access: `settings.redis_config.host`, `settings.openai_config.api_key`

### SettingsBase API

```python
class SettingsBase(BaseSettings):
    """Base class for app-level Settings with shared config and helpers."""

    # Default model_config (can be overridden)
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
        env_file_encoding="utf-8",
    )

    # Shared helper method
    def _load_config(
        self,
        config_class: type[T],
        prefix: str = "",
        env_file: str | None = None,
    ) -> T:
        """Load domain config from environment with .env file support."""
        return config_class.from_env(prefix=prefix, env_file=env_file)
```

### Overriding model_config (if needed)

```python
class CustomSettings(SettingsBase):
    model_config = SettingsConfigDict(
        env_file="custom.env",  # Override env file
        case_sensitive=True,     # Override case sensitivity
        extra="allow",           # Override extra fields
    )
```

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
    prefix: str = "",            # e.g., "REDIS_"
    separator: str = "_",        # Field separator
    max_depth: int = 3,          # Max nesting depth
    env_file: str | None = None, # Path to .env file (optional)
    **defaults: Any              # Fallback values
)
```

**Precedence**: `os.environ` > `.env file` > `defaults`

Type coercion: `bool` (true/1/yes/on), `int`, `float`, `list` (comma-separated)

## Key Principles

1. **No field duplication**: Define fields once in ConfigBase, not in Settings
2. **No config duplication**: Use SettingsBase to inherit `model_config` and `_load_config()`
3. **Explicit loading**: `from_env()` makes env loading clear and intentional
4. **Precedence clarity**: `os.environ` > `.env file` > `defaults`
5. **Single source of truth**: Domain config fields live in ConfigBase classes
6. **Testing friendly**: Direct instantiation works without environment setup
7. **FastAPI compatible**: All ConfigBase classes work as request bodies

## Migration Pattern: BaseSettings → SettingsBase

**Before** (with duplication):
```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(  # DUPLICATED across services
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )

    redis_host: str = "localhost"       # DUPLICATED field
    redis_port: int = 6379              # DUPLICATED field

    @cached_property
    def redis_config(self) -> RedisConfig:
        # DUPLICATED helper logic
        return RedisConfig.from_env(prefix="REDIS_")
```

**After** (zero duplication):
```python
from air_common import SettingsBase

class Settings(SettingsBase):  # Inherits everything
    # NO model_config - inherited!
    # NO duplicated fields!
    # NO duplicated helper - inherited _load_config()!

    worker_slots: int = 5  # App-level only

    @cached_property
    def redis_config(self) -> RedisConfig:
        return self._load_config(RedisConfig, prefix="REDIS_")
```
