"""Structured logging configuration using structlog."""

import json
import logging
import os
import sys
from pathlib import Path
from typing import Any

import structlog
import yaml
from dotenv import load_dotenv
from structlog.types import EventDict, Processor


def _load_dotenv_file() -> None:
    """Load .env file from current or parent directories."""
    _env_path = Path.cwd() / ".env"
    if _env_path.exists():
        load_dotenv(_env_path, override=True)
    else:
        for parent in Path.cwd().parents:
            _env_path = parent / ".env"
            if _env_path.exists():
                load_dotenv(_env_path, override=True)
                break


def _load_logging_levels_from_file(file_path: str) -> dict[str, str] | None:
    """Load logger levels from JSON or YAML file.

    File format is determined by extension:
    - .json: Parse as JSON
    - .yaml, .yml: Parse as YAML

    Args:
        file_path: Path to logger levels file

    Returns:
        Dict of logger name -> level, or None if file not found or parsing fails
    """
    # Resolve path (relative paths are resolved from cwd)
    path = Path(file_path) if Path(file_path).is_absolute() else Path.cwd() / file_path

    # Check if file exists
    if not path.exists():
        sys.stderr.write(f"Warning: Logger levels file not found: {path}\n")
        return None

    try:
        content = path.read_text(encoding="utf-8")
    except Exception as e:
        sys.stderr.write(
            f"Warning: Failed to read logger levels file {file_path}: {e}\n"
        )
        return None

    # Parse based on file extension
    parsed: dict[str, Any] | None = None
    suffix = path.suffix.lower()

    try:
        if suffix == ".json":
            parsed = json.loads(content)
        elif suffix in (".yaml", ".yml"):
            parsed = yaml.safe_load(content)
        else:
            sys.stderr.write(
                f"Warning: Unsupported file extension: {suffix} "
                f"(use .json, .yaml, or .yml)\n"
            )
            return None
    except (json.JSONDecodeError, yaml.YAMLError) as e:
        sys.stderr.write(
            f"Warning: Failed to parse logger levels file {file_path}: {e}\n"
        )
        return None

    if parsed is None or not isinstance(parsed, dict):
        sys.stderr.write(
            f"Warning: Logger levels file must contain a dict, got {type(parsed)}\n"
        )
        return None

    # Flatten nested YAML structure and normalize WARN -> WARNING
    flattened = _flatten_yaml_dict(parsed)
    return {
        name: "WARNING" if level.upper() == "WARN" else level.upper()
        for name, level in flattened.items()
    }


def _flatten_yaml_dict(data: dict[str, Any], parent_key: str = "") -> dict[str, str]:
    """Flatten nested YAML dict to dotted logger names.

    Example:
        {"uvicorn": {"error": "INFO"}} -> {"uvicorn.error": "INFO"}
        {"uvicorn": "INFO"} -> {"uvicorn": "INFO"}
    """
    result: dict[str, str] = {}
    for key, value in data.items():
        new_key = f"{parent_key}.{key}" if parent_key else key

        if isinstance(value, dict):
            # Nested structure: uvicorn:\n  error: INFO
            result.update(_flatten_yaml_dict(value, new_key))
        elif isinstance(value, str):
            # Direct value: uvicorn.error: INFO or uvicorn: INFO
            result[new_key] = value
        else:
            sys.stderr.write(
                f"Warning: Invalid logger level type for {new_key}: {type(value)}\n"
            )

    return result


def _load_logging_levels_from_env() -> dict[str, str] | None:
    """Load logger levels from environment variables.

    Priority order:
    1. LOGGING_LEVELS_FILE: Path to JSON/YAML file
    2. LOGGING_LEVELS: Inline JSON or YAML string

    LOGGING_LEVELS supports both JSON and YAML formats:
    - JSON: {"uvicorn.error": "INFO", "httpx": "WARNING"}
    - YAML flat: "uvicorn.error: INFO\\nhttpx: WARNING"
    - YAML nested: "uvicorn:\\n  error: INFO\\nhttpx: WARNING"

    Returns None if not set or parsing fails.
    Normalizes WARN -> WARNING for consistency.
    """
    # Check LOGGING_LEVELS_FILE first (higher priority)
    file_path = os.getenv("LOGGING_LEVELS_FILE")
    if file_path:
        result = _load_logging_levels_from_file(file_path)
        if result is not None:
            return result
        # If file loading fails, fall through to LOGGING_LEVELS

    # Check LOGGING_LEVELS (inline configuration)
    env_value = os.getenv("LOGGING_LEVELS")
    if not env_value:
        return None

    parsed: dict[str, Any] | None = None

    # Try JSON first
    try:
        parsed = json.loads(env_value)
    except json.JSONDecodeError:
        # Try YAML if JSON fails
        try:
            parsed = yaml.safe_load(env_value)
        except yaml.YAMLError as e:
            sys.stderr.write(
                f"Warning: Failed to parse LOGGING_LEVELS as JSON or YAML: {e}\n"
            )
            return None

    if parsed is None or not isinstance(parsed, dict):
        sys.stderr.write(
            f"Warning: LOGGING_LEVELS must be a dict, got {type(parsed)}\n"
        )
        return None

    # Flatten nested YAML structure
    flattened = _flatten_yaml_dict(parsed)

    # Normalize WARN -> WARNING
    return {
        name: "WARNING" if level.upper() == "WARN" else level.upper()
        for name, level in flattened.items()
    }


def add_log_level(
    _logger: logging.Logger, method_name: str, event_dict: EventDict
) -> EventDict:
    """Add log level to event dict (structlog processor)."""
    if method_name == "warn":
        method_name = "warning"
    event_dict["level"] = method_name.upper()
    return event_dict


def add_caller_info(
    _logger: logging.Logger, _method_name: str, event_dict: EventDict
) -> EventDict:
    """Add caller info (file, line, thread) from LogRecord (zero overhead).

    Python's logging already collects caller info via findCaller() when creating
    LogRecord. This processor extracts that pre-collected data from LogRecord
    instead of performing expensive frame introspection again.

    Performance: ~170-420x faster than frame introspection (0.5µs vs 85-210µs per log)
    """
    record: logging.LogRecord | None = event_dict.get("_record")

    if record is not None:
        # Extract pre-collected caller info from LogRecord (no frame walking)
        event_dict["filename"] = record.filename  # Already basename
        event_dict["lineno"] = record.lineno
        event_dict["function"] = record.funcName
        event_dict["thread"] = record.threadName  # Already collected

    return event_dict


def render_to_plain_text(
    _logger: logging.Logger, _method_name: str, event_dict: EventDict
) -> str:
    """Render plain text log (for non-TTY output)."""
    timestamp = event_dict.get("timestamp", "")
    level = event_dict.get("level", "INFO")
    thread = event_dict.get("thread", "MainThread")
    logger_name = event_dict.get("logger", "")
    lineno = event_dict.get("lineno", "")
    event = event_dict.get("event", "")
    exception = event_dict.get("exception", "")

    # Truncate microseconds to milliseconds
    if len(timestamp) > 23:
        timestamp = timestamp[:23]

    log_line = f"{timestamp} [{level:8s}] [{thread}] [{logger_name}:{lineno}] {event}"

    # Append additional context fields (excluding standard fields)
    standard_fields = {
        "timestamp",
        "level",
        "thread",
        "logger",
        "lineno",
        "event",
        "exception",
        "filename",
        "function",
        "_record",
        "_from_structlog",
    }
    extra_fields = {k: v for k, v in event_dict.items() if k not in standard_fields}
    if extra_fields:
        for key, value in extra_fields.items():
            log_line += f" {key}={value}"

    # Append exception traceback if present
    if exception:
        log_line += f"\n{exception}"

    return log_line


def render_colored_log(
    _logger: logging.Logger, _method_name: str, event_dict: EventDict
) -> str:
    """Render colored log for terminal output."""
    # ANSI codes
    RESET = "\033[0m"
    DIM = "\033[2m"
    BLUE = "\033[34m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_BLACK = "\033[90m"
    WHITE = "\033[97m"
    CYAN = "\033[36m"
    YELLOW = "\033[33m"

    LEVEL_COLORS = {
        "DEBUG": "\033[36m",
        "INFO": "\033[32m",
        "WARNING": "\033[33m",
        "ERROR": "\033[31m",
        "CRITICAL": "\033[35m\033[1m",
    }

    timestamp = event_dict.get("timestamp", "")
    level = event_dict.get("level", "INFO")
    thread = event_dict.get("thread", "MainThread")
    logger_name = event_dict.get("logger", "")
    lineno = event_dict.get("lineno", "")
    event = event_dict.get("event", "")
    exception = event_dict.get("exception", "")

    if len(timestamp) > 23:
        timestamp = timestamp[:23]

    level_color = LEVEL_COLORS.get(level, RESET)

    log_line = (
        f"{DIM}{timestamp}{RESET} "
        f"[{level_color}{level:8s}{RESET}] "
        f"[{BLUE}{thread}{RESET}] "
        f"[{BRIGHT_MAGENTA}{logger_name}{RESET}:{BRIGHT_BLACK}{lineno}{RESET}] "
        f"{WHITE}{event}{RESET}"
    )

    # Append additional context fields (excluding standard fields)
    standard_fields = {
        "timestamp",
        "level",
        "thread",
        "logger",
        "lineno",
        "event",
        "exception",
        "filename",
        "function",
        "_record",
        "_from_structlog",
    }
    extra_fields = {k: v for k, v in event_dict.items() if k not in standard_fields}
    if extra_fields:
        for key, value in extra_fields.items():
            log_line += f" {CYAN}{key}{RESET}={YELLOW}{value}{RESET}"

    # Append exception traceback if present
    if exception:
        log_line += f"\n{exception}"

    return log_line


def configure_logging(
    log_level: str = "INFO",
    log_file: str | None = None,
    log_file_level: str = "WARNING",
    logging_levels: dict[str, str] | None = None,
) -> None:
    """Configure structured logging with unified format across all loggers.

    Similar to Java's SLF4J + Logback pattern. Configures root logger to ensure
    all libraries (uvicorn, FastAPI, langchain, etc.) use the same format.

    Args:
        log_level: Console log level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional JSON log file path
        log_file_level: Log level for file (default: WARNING)
        logging_levels: Per-logger levels (hierarchical, like Spring Boot's
            logging.level). Example: {"uvicorn": "WARNING", "langchain": "INFO"}
            If None, reads from LOGGING_LEVELS environment variable
    """
    # Load .env file for environment variables
    _load_dotenv_file()

    # Load logging levels from env if not provided
    if logging_levels is None:
        logging_levels = _load_logging_levels_from_env()

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    root_logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    root_logger.addHandler(console_handler)

    # File handler (JSON format)
    file_handler = None
    if log_file:
        try:
            # Ensure log directory exists (creates parent directories automatically)
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(getattr(logging, log_file_level.upper()))
            root_logger.addHandler(file_handler)
        except PermissionError as e:
            sys.stderr.write(
                f"Warning: Permission denied to create log file {log_file}: {e}\n"
            )
            file_handler = None
        except Exception as e:
            sys.stderr.write(f"Warning: Failed to create log file {log_file}: {e}\n")
            file_handler = None

    # Structlog processors
    timestamper = structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S.%f")
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        add_log_level,
        add_caller_info,
        timestamper,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    # Console formatter (colored for TTY, plain for pipes)
    use_colors = sys.stdout.isatty()
    console_processor = render_colored_log if use_colors else render_to_plain_text
    console_formatter = structlog.stdlib.ProcessorFormatter(
        processor=console_processor,
        foreign_pre_chain=shared_processors,
    )
    console_handler.setFormatter(console_formatter)

    # File formatter (JSON)
    if file_handler:
        json_formatter = structlog.stdlib.ProcessorFormatter(
            processor=structlog.processors.JSONRenderer(),
            foreign_pre_chain=shared_processors,
        )
        file_handler.setFormatter(json_formatter)

    # Configure structlog
    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Apply per-logger levels (hierarchical: "uvicorn" affects "uvicorn.*")
    if logging_levels:
        for logger_name, level in logging_levels.items():
            logger = logging.getLogger(logger_name)
            logger.setLevel(getattr(logging, level.upper()))
            logger.propagate = True


def reconfigure_existing_loggers() -> None:
    """Reconfigure existing loggers to inherit parent levels (hierarchical).

    Call after third-party libraries initialize their loggers.
    Example: "uvicorn" WARNING affects "uvicorn.error", "uvicorn.access"
    """
    for logger_name in list(logging.Logger.manager.loggerDict.keys()):
        logger = logging.getLogger(logger_name)

        # Clear handlers, use root logger's handlers
        if logger.handlers:
            logger.handlers.clear()
        logger.propagate = True

        # Inherit parent level (hierarchical)
        parts = logger_name.split(".")
        for i in range(len(parts) - 1, 0, -1):
            parent_name = ".".join(parts[:i])
            parent_logger = logging.getLogger(parent_name)
            if parent_logger.level != logging.NOTSET:
                logger.setLevel(parent_logger.level)
                break


def get_logger(name: str) -> Any:
    """Get a structured logger instance.

    Args:
        name: Logger name

    Returns:
        Structlog logger instance
    """
    return structlog.get_logger(name)
