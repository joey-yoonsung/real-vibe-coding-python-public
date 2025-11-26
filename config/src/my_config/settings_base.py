"""Base settings class with ConfigBase loading helper.

This module provides a base class for application settings that eliminates
duplication when loading ConfigBase instances from environment variables.
"""

from typing import Any, TypeVar

from pydantic_settings import BaseSettings, SettingsConfigDict

from my_config.config_base import ConfigBase

T = TypeVar("T", bound=ConfigBase)


class SettingsBase(BaseSettings):
    """Base class for application settings with ConfigBase loading helper.

    This class provides:
    1. Default `model_config` with sensible settings for all services
    2. `_load_config()` helper method for loading ConfigBase instances

    The default model_config can be overridden by child classes if needed.

    Default Configuration:
        - env_file: ".env" (reads from .env file in current directory)
        - env_file_encoding: "utf-8"
        - case_sensitive: False (environment variables are case-insensitive)
        - extra: "ignore" (ignore extra fields not defined in model)

    Example (using defaults):
        >>> from functools import cached_property
        >>> from pydantic import Field
        >>>
        >>> class RedisConfig(ConfigBase):
        ...     host: str = "localhost"
        ...     port: int = 6379
        ...
        >>> class Settings(SettingsBase):
        ...     # No need to define model_config - uses defaults!
        ...     worker_slots: int = Field(default=5)
        ...
        ...     @cached_property
        ...     def redis_config(self) -> RedisConfig:
        ...         return self._load_config(RedisConfig, prefix="REDIS_")
        ...
        >>> settings = Settings()
        >>> redis = settings.redis_config
        >>> print(redis.host)  # Loaded from REDIS_HOST env var or .env file
        localhost

    Example (overriding defaults):
        >>> class Settings(SettingsBase):
        ...     model_config = SettingsConfigDict(
        ...         env_file=".env.production",  # Override env file
        ...         case_sensitive=True,          # Override case sensitivity
        ...     )
        ...     worker_slots: int = Field(default=5)

    Benefits:
        - Default config eliminates duplication across services
        - Single source of truth: `env_file` defined once
        - Helper method reused across all config properties
        - Type-safe: Proper generic typing with TypeVar
        - Clean code: One-liner for each config property
        - IDE support: Full autocomplete and type inference
        - Flexible: Child classes can override any config setting
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    def _load_config(
        self,
        config_class: type[T],
        prefix: str,
        **kwargs: Any,
    ) -> T:
        """Load a ConfigBase instance using Settings' model_config.

        This helper method extracts `env_file` from `model_config` and passes
        it to `ConfigBase.from_env()`, eliminating the need to repeat this
        logic in every `@cached_property` method.

        Args:
            config_class: ConfigBase subclass to instantiate
            prefix: Environment variable prefix (e.g., "REDIS_", "OPENAI_")
            **kwargs: Additional arguments passed to ConfigBase.from_env()

        Returns:
            Instance of config_class loaded from env_file + environment variables

        Example:
            >>> @cached_property
            ... def redis_config(self) -> RedisConfig:
            ...     return self._load_config(RedisConfig, prefix="REDIS_")
        """
        env_file_raw = self.model_config.get("env_file")

        # Convert to string if needed
        # SettingsConfigDict.env_file can be: str | Path | Sequence[Path | str]
        env_file: str | None = None
        if env_file_raw:
            if isinstance(env_file_raw, str):
                env_file = env_file_raw
            elif hasattr(env_file_raw, "__fspath__"):  # Path-like object
                env_file = str(env_file_raw)
            # Note: If env_file is a sequence, we only use the first entry
            # This matches typical BaseSettings behavior
            elif isinstance(env_file_raw, (list, tuple)) and env_file_raw:
                first_entry = env_file_raw[0]
                if isinstance(first_entry, str):
                    env_file = first_entry
                elif hasattr(first_entry, "__fspath__"):
                    env_file = str(first_entry)

        return config_class.from_env(prefix=prefix, env_file=env_file, **kwargs)
