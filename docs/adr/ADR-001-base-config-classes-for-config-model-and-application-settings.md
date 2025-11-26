# ADR-001: Base Config Classes for Config Model and Application Settings

## Status

Accepted

## Date

2024-12-14

## Context

This project needs a configuration management system that meets the following requirements:

1. **Framework Compatibility**: Configuration classes must work seamlessly with FastAPI (request/response models) and LangGraph (state classes)
2. **Environment Variable Loading**: Support for loading configuration from environment variables and `.env` files
3. **Type Safety**: Full Pydantic validation and type inference support
4. **Sensitive Data Handling**: Ability to mask sensitive fields (passwords, API keys) in logs
5. **Nested Configuration**: Support for hierarchical configuration structures
6. **Code Reusability**: Eliminate duplication when loading domain-specific configs across multiple services

Using a single configuration class (e.g., just `BaseSettings`) creates problems:
- `BaseSettings` automatically loads from environment variables on instantiation, which breaks FastAPI/LangGraph compatibility
- Mixing app-level settings with domain configs leads to tight coupling
- Repeated boilerplate code for loading each domain config with the correct prefix

## Decision

We implement a **two-type configuration system**:

### 1. ConfigBase (inherits from `pydantic.BaseModel`)

For domain-specific configurations (Redis, OpenAI, S3, Database, etc.)

```python
class ConfigBase(BaseModel):
    model_config = ConfigDict(extra="allow", validate_assignment=True)

    @classmethod
    def from_env(cls, prefix: str, ...) -> T:
        """Explicitly load from environment variables"""

    def get_printable_config(self) -> dict[str, Any]:
        """Return config with sensitive fields masked"""
```

Key characteristics:
- Does NOT auto-load from environment variables
- Requires explicit `from_env()` call to load from environment
- Compatible with FastAPI request/response models
- Compatible with LangGraph state classes
- Supports extra fields (`extra="allow"`)
- Supports nested models up to 3 levels deep

### 2. SettingsBase (inherits from `pydantic_settings.BaseSettings`)

For application-level settings that orchestrate domain configs

```python
class SettingsBase(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    def _load_config(self, config_class: type[T], prefix: str) -> T:
        """Helper to load ConfigBase instances with consistent env_file"""
```

Key characteristics:
- Auto-loads from `.env` file and environment variables
- Provides default `model_config` for all services
- `_load_config()` helper eliminates duplication when loading domain configs
- Single source of truth for `env_file` setting

### Usage Pattern

```python
class RedisConfig(ConfigBase):
    host: str = "localhost"
    port: int = 6379

class OpenAIConfig(ConfigBase):
    api_key: str
    model: str = "gpt-4"

class Settings(SettingsBase):
    worker_slots: int = 5

    @cached_property
    def redis(self) -> RedisConfig:
        return self._load_config(RedisConfig, prefix="REDIS_")

    @cached_property
    def openai(self) -> OpenAIConfig:
        return self._load_config(OpenAIConfig, prefix="OPENAI_")
```

## Rationale

### Why separate ConfigBase from SettingsBase?

1. **Separation of Concerns**
   - `SettingsBase`: Application lifecycle (when to load, which env file)
   - `ConfigBase`: Domain knowledge (what fields, validation rules)

2. **Framework Compatibility**
   - `BaseSettings` auto-loads on instantiation, breaking FastAPI/LangGraph
   - `BaseModel` requires explicit loading, preserving framework compatibility

3. **Explicit is Better than Implicit**
   - Environment loading happens only when explicitly requested via `from_env()`
   - No hidden side effects during class instantiation

4. **Code Reuse**
   - `_load_config()` helper in SettingsBase eliminates repeated boilerplate
   - Consistent `env_file` handling across all domain configs

## Alternatives Considered

### Single BaseSettings-based Configuration

- Pros: Simpler, fewer classes
- Cons: Breaks FastAPI/LangGraph compatibility, auto-loading side effects
- Why rejected: Framework compatibility is a hard requirement

### Dynaconf or python-dotenv Direct Usage

- Pros: Well-established libraries
- Cons: No Pydantic validation, less type safety, no IDE support
- Why rejected: Type safety and IDE support are essential for maintainability

### Environment-only Configuration (No .env Files)

- Pros: Simpler, follows 12-factor app principles strictly
- Cons: Poor developer experience, hard to manage local development
- Why rejected: Developer experience matters; `.env` files are standard practice

## Consequences

### Positive

- Full FastAPI and LangGraph compatibility maintained
- Type-safe configuration with IDE autocomplete
- Sensitive fields automatically masked in logs
- Consistent loading pattern across all services
- Nested configuration support up to 3 levels
- Extra fields supported for flexibility

### Negative

- Two classes to understand instead of one
- Slightly more boilerplate for simple use cases
- Developers must remember to use `from_env()` explicitly

### Risks

- Future Pydantic major version changes may require updates
- Nested configuration depth limit (3 levels) may need adjustment for complex configs
