"""Base configuration class with environment variable loading support."""

import os
import typing
from typing import Any, TypeVar, get_args, get_origin

from pydantic import BaseModel, ConfigDict

from my_logger import get_logger

T = TypeVar("T", bound="ConfigBase")

logger = get_logger(__name__)


class ConfigBase(BaseModel):
    """Base configuration class with extra fields and env loading support.

    Features:
    - Supports extra fields (kwargs) via extra="allow"
    - Provides from_env() class method for loading from environment variables
    - Supports nested models up to 3 levels deep with double separator notation
    - Provides get_printable_config() for masked sensitive field output
    - Full Pydantic validation and type safety

    Important Design Decision:
    This class inherits from BaseModel (not BaseSettings) to ensure:
    - FastAPI compatibility (request/response models)
    - LangGraph state class compatibility
    - Explicit environment loading only when needed
    - No automatic env var loading on instantiation
    """

    model_config = ConfigDict(
        extra="allow",
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    def get_extra_configs(self) -> dict[str, Any]:
        """Get all extra (non-declared) fields.

        Returns:
            Dictionary containing only extra fields (not declared in model_fields)
        """
        return {
            k: v
            for k, v in self.model_dump().items()
            if k not in self.__class__.model_fields
        }

    def get_printable_config(self) -> dict[str, Any]:
        """Get printable representation with sensitive values masked.

        Sensitive fields are detected by key postfix:
        - *password, *pw, *key, *secret, *credentials

        Returns:
            Dictionary with sensitive fields masked
        """
        config_dict = self.model_dump()

        def is_sensitive(key: str) -> bool:
            """Check if key is sensitive based on postfix."""
            key_lower = key.lower()
            sensitive_postfixes = ("password", "pw", "key", "secret", "credentials")
            return any(key_lower.endswith(postfix) for postfix in sensitive_postfixes)

        def mask_value(value: Any) -> str:
            """Mask sensitive value."""
            if value is None or value == "":
                return "<not set>"
            if not isinstance(value, str):
                return "****"
            if len(value) <= 4:
                return "****"
            return f"{value[:2]}...{value[-2:]}"

        # Apply masking to sensitive fields
        return {
            k: mask_value(v) if is_sensitive(k) else v for k, v in config_dict.items()
        }

    @classmethod
    def from_env(
        cls: type[T],
        prefix: str = "",
        separator: str = "_",
        max_depth: int = 3,
        **defaults: Any,
    ) -> T:
        """Load configuration from environment variables with nested model support.

        This method supports nested models up to specified depth using double
        separator notation. For example, with separator="_", use "__" to
        indicate nested fields.

        Args:
            prefix: Environment variable prefix (e.g., "REDIS_")
            separator: Separator for field names (default: "_")
                      - Single separator: Used for multi-word field names
                      - Double separator: Used to indicate nested models
            max_depth: Maximum nesting depth for nested models (default: 3)
            **defaults: Default values if env var not found

        Returns:
            Instance of the config class loaded from environment

        Examples:
            Simple Configuration:
            >>> class RedisConfig(ConfigBase):
            ...     host: str = "localhost"
            ...     port: int = 6379
            ...     max_connections: int = 100  # Note: underscore in field name
            ...
            >>> # Environment variables:
            >>> # REDIS_HOST=redis.example.com
            >>> # REDIS_PORT=6380
            >>> # REDIS_MAX_CONNECTIONS=200
            >>> config = RedisConfig.from_env(prefix="REDIS_")
            >>> print(config.host)  # "redis.example.com"
            >>> print(config.max_connections)  # 200

            1-Level Nested Configuration:
            >>> class PoolConfig(BaseModel):
            ...     max_size: int = 10
            ...     min_size: int = 2
            ...     timeout: float = 30.0
            ...
            >>> class DatabaseConfig(ConfigBase):
            ...     host: str
            ...     port: int = 5432
            ...     pool: PoolConfig = PoolConfig()  # Nested model
            ...
            >>> # Environment variables:
            >>> # DB_HOST=db.example.com
            >>> # DB_PORT=3306
            >>> # DB_POOL__MAX_SIZE=50    # field name + double underscore
            >>> # DB_POOL__MIN_SIZE=5     # pool.min_size
            >>> # DB_POOL__TIMEOUT=60.5   # pool.timeout
            >>> config = DatabaseConfig.from_env(prefix="DB_")
            >>> print(config.host)  # "db.example.com"
            >>> print(config.pool.max_size)  # 50
            >>> print(config.pool.timeout)  # 60.5

            3-Level Deep Nested Configuration:
            >>> class RetryConfig(BaseModel):
            ...     max_attempts: int = 3
            ...     backoff_factor: float = 2.0
            ...
            >>> class ConnectionConfig(BaseModel):
            ...     timeout: int = 30
            ...     retry: RetryConfig = RetryConfig()
            ...
            >>> class DatabaseConfig(BaseModel):
            ...     host: str = "localhost"
            ...     connection: ConnectionConfig = ConnectionConfig()
            ...
            >>> class AppConfig(ConfigBase):
            ...     name: str
            ...     database: DatabaseConfig = DatabaseConfig()
            ...
            >>> # Environment variables (3 levels deep):
            >>> # APP_NAME=myapp
            >>> # APP_DATABASE__HOST=db.example.com
            >>> # APP_DATABASE__CONNECTION__TIMEOUT=60
            >>> # APP_DATABASE__CONNECTION__RETRY__MAX_ATTEMPTS=5
            >>> # APP_DATABASE__CONNECTION__RETRY__BACKOFF_FACTOR=1.5
            >>> config = AppConfig.from_env(prefix="APP_")
            >>> print(config.name)  # "myapp"
            >>> print(config.database.host)  # "db.example.com"
            >>> print(config.database.connection.timeout)  # 60
            >>> print(config.database.connection.retry.max_attempts)  # 5
            >>> print(config.database.connection.retry.backoff_factor)  # 1.5

            Extra Fields:
            >>> # Environment variables:
            >>> # APP_HOST=localhost
            >>> # APP_DEBUG_MODE=true      # Not declared in model
            >>> # APP_CUSTOM_SETTING=value # Not declared in model
            >>> config = AppConfig.from_env(prefix="APP_")
            >>> print(config.debug_mode)  # "true" (as string, extra field)
            >>> print(config.get_extra_configs())  # {"debug_mode": "true", ...}

            Different Separators:
            >>> # Using dot separator (though not recommended for env vars)
            >>> # Environment variables:
            >>> # DB.HOST=localhost
            >>> # DB.POOL..MAX.SIZE=100  # Double separator for nesting
            >>> config = DatabaseConfig.from_env(prefix="DB.", separator=".")
        """
        env_values: dict[str, Any] = {}
        prefix_upper = prefix.upper()
        double_separator = separator * 2  # e.g., "__" for nested fields

        # Collect all relevant environment variables
        env_vars: dict[str, str] = {}
        for env_key, env_value in os.environ.items():
            if prefix_upper:
                # If prefix is provided, only collect vars starting with prefix
                if env_key.startswith(prefix_upper):
                    key_without_prefix = env_key[len(prefix_upper) :]
                    env_vars[key_without_prefix] = env_value
            else:
                # If no prefix, collect all environment variables
                env_vars[env_key] = env_value

        # Build a tree structure from environment variables for nested processing
        env_tree = _build_env_tree(env_vars, double_separator)

        # Process fields recursively
        env_values = _process_fields_recursive(
            cls.model_fields, env_tree, defaults, separator, max_depth=max_depth
        )

        return cls(**env_values)


def _build_env_tree(
    env_vars: dict[str, str],
    double_separator: str,
) -> dict[str, Any]:
    """Build a tree structure from flat environment variables.

    Args:
        env_vars: Flat dictionary of environment variables (prefix already removed)
        double_separator: Double separator for nesting (e.g., "__")

    Returns:
        Tree structure representing nested configuration

    Example:
        Input: {"DATABASE__HOST": "localhost", "DATABASE__CONNECTION__TIMEOUT": "60"}
        Output: {"DATABASE": {"HOST": "localhost", "CONNECTION": {"TIMEOUT": "60"}}}
    """
    tree: dict[str, Any] = {}

    for key, value in env_vars.items():
        # Split by double separator to get nesting levels
        if double_separator in key:
            parts = key.split(double_separator)
            current = tree

            # Navigate/create tree structure
            for _, part in enumerate(parts[:-1]):
                if part not in current:
                    current[part] = {}
                elif not isinstance(current[part], dict):
                    # If there's a value already, convert to dict with special key
                    current[part] = {"__value__": current[part]}
                current = current[part]

            # Set the final value
            final_key = parts[-1]
            current[final_key] = value
        else:
            # Simple key-value
            tree[key] = value

    return tree


def _process_fields_recursive(  # noqa: PLR0912, PLR0913
    model_fields: dict[str, Any],
    env_tree: dict[str, Any],
    defaults: dict[str, Any],
    separator: str,
    current_depth: int = 0,
    max_depth: int = 3,
) -> dict[str, Any]:
    """Recursively process model fields from environment tree.

    Args:
        model_fields: Pydantic model fields to process
        env_tree: Tree structure of environment variables
        defaults: Default values
        separator: Field separator
        current_depth: Current nesting depth (for limiting recursion)
        max_depth: Maximum allowed nesting depth

    Returns:
        Dictionary of processed field values
    """
    result: dict[str, Any] = {}

    for field_name, field_info in model_fields.items():
        field_type = field_info.annotation
        origin = get_origin(field_type)

        # Convert field name to env key format
        if separator == "_":
            env_key = field_name.upper()
        else:
            env_key = field_name.replace("_", separator).upper()

        # Extract actual type from Optional if needed
        actual_field_type = field_type
        if origin is not None:
            # Handle Optional[T] which is Union[T, None]
            args = get_args(field_type)
            if args and len(args) == 2 and type(None) in args:
                # This is Optional[T], extract T
                actual_field_type = args[0] if args[1] is type(None) else args[1]

        # Check if it's a nested BaseModel (including Optional[BaseModel])
        if isinstance(actual_field_type, type) and issubclass(
            actual_field_type, BaseModel
        ):
            # Check if we've exceeded max depth
            if current_depth >= max_depth:
                # Log warning about max depth exceeded
                logger.warning(
                    f"Max depth ({max_depth}) exceeded for nested field "
                    f"'{field_name}' at depth {current_depth}. "
                    f"Field will be treated as a simple value."
                )
                # Treat as simple field when max depth is exceeded
                if env_key in env_tree and not isinstance(env_tree[env_key], dict):
                    result[field_name] = _coerce_type(env_tree[env_key], field_type)
                elif field_name in defaults:
                    result[field_name] = defaults[field_name]
            # Handle nested model within depth limit
            elif env_key in env_tree and isinstance(env_tree[env_key], dict):
                # Recursively process nested fields
                nested_values = {}

                if hasattr(actual_field_type, "model_fields"):
                    nested_values = _process_fields_recursive(
                        actual_field_type.model_fields,
                        env_tree[env_key],
                        {},  # No defaults for nested fields
                        separator,
                        current_depth + 1,
                        max_depth,
                    )

                # Also process extra fields in the nested tree
                for sub_key, sub_value in env_tree[env_key].items():
                    sub_field_name = sub_key.lower()
                    if separator != "_":
                        sub_field_name = sub_field_name.replace(separator, "_")

                    if sub_field_name not in nested_values and not isinstance(
                        sub_value, dict
                    ):
                        # Add extra field (no type coercion for unknown fields)
                        nested_values[sub_field_name] = sub_value

                if nested_values:
                    result[field_name] = actual_field_type(**nested_values)
                elif field_name in defaults:
                    result[field_name] = defaults[field_name]
            elif field_name in defaults:
                result[field_name] = defaults[field_name]
        # Handle simple field
        elif env_key in env_tree and not isinstance(env_tree[env_key], dict):
            result[field_name] = _coerce_type(env_tree[env_key], field_type)
        elif field_name in defaults:
            result[field_name] = defaults[field_name]

    # Process extra fields (not in model_fields)
    for env_key, env_value in env_tree.items():
        if separator == "_":
            field_name = env_key.lower()
        else:
            field_name = env_key.replace(separator, "_").lower()

        if field_name not in result and not isinstance(env_value, dict):
            # Add as extra field (string value)
            result[field_name] = env_value

    return result


def _coerce_type(value: str, field_type: Any) -> Any:
    """Coerce string value to appropriate type.

    Args:
        value: String value from environment variable
        field_type: Target type annotation

    Returns:
        Coerced value in the appropriate type

    Examples:
        >>> _coerce_type("true", bool)  # True
        >>> _coerce_type("123", int)    # 123
        >>> _coerce_type("1.5", float)  # 1.5
        >>> _coerce_type("a,b,c", list[str])  # ["a", "b", "c"]
    """
    origin = get_origin(field_type)

    # Handle Union types (including Optional)
    if origin is typing.Union:
        args = get_args(field_type)
        non_none_types = [arg for arg in args if arg is not type(None)]
        if non_none_types:
            field_type = non_none_types[0]
            origin = get_origin(field_type)  # Re-evaluate origin after unwrapping Union

    # Type coercion
    if field_type is bool:
        return value.lower() in ("true", "1", "yes", "on")
    elif field_type is int:
        return int(value)
    elif field_type is float:
        return float(value)
    elif origin is list:
        # Handle list type - split by comma
        return [item.strip() for item in value.split(",") if item.strip()]
    else:
        # Return as string for any other type
        return value
