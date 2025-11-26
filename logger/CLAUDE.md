# AIR Logger

Shared structured logging module for AIR services using structlog.

## Features

- **Dual Output**: Console (colored) + optional JSON file logging
- **Colored Console**: Custom color scheme for terminal output
- **JSON File Logging**: Machine-readable logs for aggregation tools (ELK, Splunk, Datadog)
- **Separate Log Levels**: Independent level control for console and file
- **Auto-Detection**: Automatically switches between colored/plain text based on TTY
- **Auto-Directory Creation**: Automatically creates log file directories if they don't exist

## Installation

This package is part of the AIR service workspace and should be installed via workspace dependencies:

```toml
# In your service's pyproject.toml
dependencies = [
    "my-logger",
    # ... other dependencies
]

[tool.uv.sources]
my-logger = { workspace = true }
```

## Usage

### Basic Setup

```python
from my_logger import configure_logging, get_logger

# Configure logging (typically in main.py or app startup)
configure_logging(
    log_level="INFO",                          # Console log level
    log_file="/var/log/myservice/app.json",   # Optional: JSON file path
    log_file_level="WARNING",                  # Optional: File log level (default: WARNING)
)

# Get logger for your module
logger = get_logger(__name__)

# Use the logger
logger.info("Application started")
logger.warning("Warning message", extra_field="value")
logger.error("Error occurred", error_code=500)
```

### Console Output

**Terminal (TTY)** - Colored format:
```
2025-11-06 05:10:54.469 [    INFO] [MainThread] [myservice.main:52] Application started
```

**Non-TTY** (e.g., piped to file) - Plain text:
```
2025-11-06 05:10:54.469 [    INFO] [MainThread] [myservice.main:52] Application started
```

### JSON File Output

When `log_file` is set, logs are written in JSON format:

```json
{
  "event": "Application started",
  "timestamp": "2025-11-06 05:10:54.469274",
  "level": "INFO",
  "logger": "myservice.main",
  "lineno": 52,
  "thread": "MainThread",
  "filename": "main.py",
  "function": "main"
}
```

## Configuration

### Parameters

- **`log_level`** (str, default: "INFO"): Console logging level (DEBUG, INFO, WARNING, ERROR)
- **`log_file`** (str | None, default: None): Path to JSON log file (optional)
  - **Auto-creates parent directories**: If the directory doesn't exist, it will be created automatically
  - **Supports nested paths**: e.g., `/var/log/myservice/2024/11/app.json` creates all intermediate directories
  - **Permission errors**: Logs warning to stderr if directory creation fails due to permissions
- **`log_file_level`** (str, default: "WARNING"): Log level for file logging
- **`logging_levels`** (dict[str, str] | None, default: None): Logger-specific log levels

### Environment Variables

```bash
# In your service configuration
LOG_LEVEL=INFO
LOG_FILE=/var/log/myservice/app.json     # Optional
LOG_FILE_LEVEL=WARNING                    # Optional

# Logger-specific levels (similar to Spring Boot's logging.level)
# Two options: inline or file-based configuration
# Priority: LOGGING_LEVELS_FILE > LOGGING_LEVELS

# Option 1: File-based configuration (recommended for complex setups)
LOGGING_LEVELS_FILE=logger-levels.yaml     # or logger-levels.json

# Option 2: Inline configuration
# JSON format (backward compatible):
LOGGING_LEVELS='{"uvicorn.access": "WARNING", "langchain": "INFO", "air_generator": "DEBUG"}'

# YAML format - Flat style (recommended):
LOGGING_LEVELS='
uvicorn.error: INFO
httpx: WARNING
langchain: DEBUG
'

# YAML format - Nested style:
LOGGING_LEVELS='
uvicorn:
  error: INFO
  access: WARNING
httpx: WARNING
'

# YAML format - Parent level (applies to all children):
LOGGING_LEVELS='
uvicorn: WARNING   # Sets WARNING for all uvicorn.* loggers
httpx: INFO
'
```

### Logger Levels File

Create a separate file for logger configuration (cleaner for complex setups):

**logger-levels.yaml** (YAML format - recommended):
```yaml
# Flat style
uvicorn.error: INFO
uvicorn.access: WARNING
httpx: WARNING
langchain: DEBUG

# Or nested style
# uvicorn:
#   error: INFO
#   access: WARNING
# httpx: WARNING
# langchain: DEBUG
```

**logger-levels.json** (JSON format):
```json
{
  "uvicorn.error": "INFO",
  "uvicorn.access": "WARNING",
  "httpx": "WARNING",
  "langchain": "DEBUG"
}
```

Then reference it in your `.env` file:
```bash
LOGGING_LEVELS_FILE=logger-levels.yaml
# or
LOGGING_LEVELS_FILE=/absolute/path/to/logger-levels.json
```

### Configuration Priority (Precedence)

Logger levels are resolved in the following priority order (highest to lowest):

1. **Code Parameter** (Highest Priority)
   ```python
   configure_logging(
       logging_levels={"uvicorn": "DEBUG"}  # Overrides all other sources
   )
   ```

2. **`.env` File: `LOGGING_LEVELS_FILE`**
   ```bash
   # In .env file
   LOGGING_LEVELS_FILE=logger-levels.yaml
   ```
   Note: `.env` file values override system environment variables (uses `override=True`)

3. **System Environment Variable: `LOGGING_LEVELS_FILE`**
   ```bash
   export LOGGING_LEVELS_FILE=/path/to/logger-levels.yaml
   ```

4. **`.env` File: `LOGGING_LEVELS`**
   ```bash
   # In .env file
   LOGGING_LEVELS='uvicorn: WARNING'
   ```

5. **System Environment Variable: `LOGGING_LEVELS`**
   ```bash
   export LOGGING_LEVELS='uvicorn: WARNING'
   ```

6. **None** (Lowest Priority)
   - No per-logger levels applied
   - Uses root logger level only

**Important**: The `.env` file is loaded with `override=True`, meaning `.env` file values take precedence over system environment variables.

**Example**:
```bash
# Terminal
export LOGGING_LEVELS_FILE=/tmp/system-levels.yaml
export LOGGING_LEVELS='uvicorn: ERROR'

# .env file
LOGGING_LEVELS_FILE=logger-levels.yaml  # ← This wins over /tmp/system-levels.yaml
LOGGING_LEVELS='uvicorn: DEBUG'         # ← Ignored because LOGGING_LEVELS_FILE is used
```

Result: Loads `logger-levels.yaml` from `.env` file (not the system env var)

### Logger-Specific Levels

Control log levels for individual loggers (similar to Java/Spring Boot's `logging.level` configuration).

**Hierarchical naming** (like Java's logback):
- Setting `"uvicorn": "WARNING"` affects `uvicorn`, `uvicorn.error`, `uvicorn.access`, etc.
- More specific names override parent: `{"uvicorn": "WARNING", "uvicorn.access": "ERROR"}`

**Via environment variable (YAML format):**
```bash
# .env file example:
LOGGING_LEVELS='
uvicorn: WARNING
langchain: INFO
air_generator: DEBUG
'
```

**Via environment variable (JSON format - backward compatible):**
```bash
export LOGGING_LEVELS='{"uvicorn": "WARNING", "langchain": "INFO"}'
```

**Via code:**
```python
configure_logging(
    log_level="INFO",
    logging_levels={
        "uvicorn": "WARNING",        # Affects all uvicorn.* loggers
        "langchain": "INFO",
        "air_generator": "DEBUG"
    }
)
```

**YAML Examples:**

1. **Flat style** (simple and clean):
```yaml
uvicorn.error: INFO
uvicorn.access: WARNING
httpx: WARNING
```

2. **Nested style** (grouped loggers):
```yaml
uvicorn:
  error: INFO
  access: WARNING
httpx: WARNING
langchain: DEBUG
```

3. **Parent level** (affects all children):
```yaml
uvicorn: WARNING    # Sets WARNING for uvicorn, uvicorn.error, uvicorn.access
httpx: INFO
```

**Default behavior:** If `LOGGING_LEVELS` is not set, no default logger levels are applied (uses root logger level only).

## Color Scheme

The console output uses a custom color scheme:

- **Timestamp**: Dim/gray
- **Log Level**:
  - DEBUG: Cyan
  - INFO: Green
  - WARNING: Yellow
  - ERROR: Red
  - CRITICAL: Magenta + Bold
- **Thread**: Blue
- **Logger name**: Light Purple
- **Line number**: Gray
- **Message**: Bright White

## Use Cases

### Development

```python
configure_logging(log_level="DEBUG")
# Console only with colored output
```

### Production

```python
configure_logging(
    log_level="INFO",
    log_file="/var/log/app.json",
    log_file_level="WARNING"
)
# Console: INFO and above (colored in terminal)
# File: WARNING and above (JSON format)
# Note: /var/log/ directory will be created automatically if it doesn't exist
```

### Production with Nested Log Paths

```python
configure_logging(
    log_level="INFO",
    log_file="/var/log/myservice/2024/11/app.json",  # Nested path
    log_file_level="WARNING"
)
# All intermediate directories (/var/log/myservice/2024/11/) are created automatically
```

### Kubernetes

```python
configure_logging(log_level="INFO")
# Console logs go to kubectl logs
# Optional: Add LOG_FILE for persistent storage
```

## Integration with Services

### Generator Service

```python
from my_logger import configure_logging, get_logger

settings = get_settings()
configure_logging(
    log_level=settings.log_level,
    log_file=settings.log_file,
    log_file_level=settings.log_file_level,
)
logger = get_logger(__name__)
```

### Gateway Service

```python
from my_logger import configure_logging, get_logger

configure_logging(log_level="INFO")
logger = get_logger(__name__)
```

### RDB Module

```python
from my_logger import get_logger

logger = get_logger(__name__)
# Configuration done by service using rdb
```

## Dependencies

- **structlog**: Structured logging library
- **python-dotenv**: .env file loading
- **pyyaml**: YAML configuration support
- Python 3.12+

## License

Internal AIR service package.
