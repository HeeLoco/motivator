"""
Logging configuration module for Motivator Bot.

Provides structured logging with support for both JSON (container-friendly) and
text (human-readable) formats. Automatically configures based on environment.

Features:
- Dual formatters: JSON for machines, text for humans
- Environment-driven configuration (LOG_LEVEL, LOG_FORMAT, LOG_FILE)
- Correlation IDs for tracking user interactions
- Container-aware (auto-detects Docker environment)
"""

import logging
import json
import os
import sys
from datetime import datetime
from typing import Optional, Dict, Any
import contextvars

# Context variable for correlation ID (thread-safe)
correlation_id_var = contextvars.ContextVar('correlation_id', default=None)


class CorrelationIDFilter(logging.Filter):
    """Add correlation ID to log records for tracking related operations."""

    def filter(self, record):
        record.correlation_id = correlation_id_var.get()
        return True


class JSONFormatter(logging.Formatter):
    """
    JSON formatter for structured logging in containers.

    Outputs logs as single-line JSON for easy parsing by log aggregation systems.
    """

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
        }

        # Add correlation ID if present
        if hasattr(record, 'correlation_id') and record.correlation_id:
            log_data['correlation_id'] = record.correlation_id

        # Add user_id if present
        if hasattr(record, 'user_id') and record.user_id:
            log_data['user_id'] = record.user_id

        # Add any extra fields passed via 'extra' parameter
        if hasattr(record, 'extra_fields'):
            log_data.update(record.extra_fields)

        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)

        # Add module and function info for DEBUG level
        if record.levelno == logging.DEBUG:
            log_data['module'] = record.module
            log_data['function'] = record.funcName
            log_data['line'] = record.lineno

        return json.dumps(log_data)


class TextFormatter(logging.Formatter):
    """
    Human-readable text formatter for development.

    Includes color coding (if terminal supports it) and structured context.
    """

    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'
    }

    def __init__(self, use_colors: bool = None):
        super().__init__()
        # Auto-detect color support if not specified
        if use_colors is None:
            use_colors = sys.stdout.isatty()
        self.use_colors = use_colors

    def format(self, record: logging.LogRecord) -> str:
        # Base format: timestamp - logger - level - message
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        level = record.levelname

        # Add color if enabled
        if self.use_colors:
            color = self.COLORS.get(level, '')
            reset = self.COLORS['RESET']
            level = f"{color}{level}{reset}"

        parts = [timestamp, record.name, level]

        # Add context information
        context_parts = []

        if hasattr(record, 'user_id') and record.user_id:
            context_parts.append(f"user:{record.user_id}")

        if hasattr(record, 'correlation_id') and record.correlation_id:
            context_parts.append(f"corr:{record.correlation_id}")

        if context_parts:
            parts.append(f"[{' | '.join(context_parts)}]")

        # Add message
        parts.append(record.getMessage())

        # Add extra fields if present
        if hasattr(record, 'extra_fields') and record.extra_fields:
            extra_str = ', '.join(f"{k}={v}" for k, v in record.extra_fields.items())
            parts.append(f"({extra_str})")

        log_line = ' - '.join(parts)

        # Add exception info if present
        if record.exc_info:
            log_line += '\n' + self.formatException(record.exc_info)

        return log_line


def setup_logging(
    log_level: Optional[str] = None,
    log_format: Optional[str] = None,
    log_file: Optional[str] = None
) -> None:
    """
    Setup logging configuration based on environment.

    Args:
        log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
                   Defaults to env var LOG_LEVEL or INFO
        log_format: Format type ('json' or 'text')
                    Defaults to env var LOG_FORMAT, or auto-detect:
                    - 'json' if running in container
                    - 'text' if running in development
        log_file: Optional log file path
                  Defaults to env var LOG_FILE
                  Disabled in container mode unless explicitly set

    Environment Variables:
        LOG_LEVEL: Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        LOG_FORMAT: Set format (json, text)
        LOG_FILE: Set log file path (empty to disable)
        CONTAINER_ENV: Set to 'true' to force container mode
    """
    # Get configuration from environment or parameters
    log_level = log_level or os.getenv('LOG_LEVEL', 'INFO').upper()

    # Detect if running in container
    is_container = (
        os.getenv('CONTAINER_ENV', '').lower() == 'true' or
        os.path.exists('/.dockerenv') or
        os.getenv('KUBERNETES_SERVICE_HOST') is not None
    )

    # Auto-detect format if not specified
    if log_format is None:
        log_format = os.getenv('LOG_FORMAT', 'json' if is_container else 'text').lower()

    # Get log file setting
    if log_file is None:
        log_file = os.getenv('LOG_FILE', '' if is_container else 'motivator_bot.log')

    # Convert log level string to logging constant
    numeric_level = getattr(logging, log_level, logging.INFO)

    # Create formatter based on format type
    if log_format == 'json':
        formatter = JSONFormatter()
    else:
        formatter = TextFormatter()

    # Configure handlers
    handlers = []

    # Always add stdout handler
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)
    stdout_handler.addFilter(CorrelationIDFilter())
    handlers.append(stdout_handler)

    # Add file handler if log_file is specified
    if log_file:
        try:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            file_handler.addFilter(CorrelationIDFilter())
            handlers.append(file_handler)
        except Exception as e:
            print(f"Warning: Could not create log file {log_file}: {e}", file=sys.stderr)

    # Configure root logger
    logging.basicConfig(
        level=numeric_level,
        handlers=handlers,
        force=True  # Override any existing configuration
    )

    # Log startup information
    logger = logging.getLogger(__name__)
    logger.info(
        "Logging configured",
        extra={'extra_fields': {
            'log_level': log_level,
            'log_format': log_format,
            'log_file': log_file if log_file else 'disabled',
            'container_mode': is_container
        }}
    )


def set_correlation_id(correlation_id: str) -> None:
    """
    Set correlation ID for the current context.

    Used to track related operations (e.g., all logs for a single user interaction).

    Args:
        correlation_id: Unique identifier for the operation
    """
    correlation_id_var.set(correlation_id)


def clear_correlation_id() -> None:
    """Clear the correlation ID for the current context."""
    correlation_id_var.set(None)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def log_with_context(
    logger: logging.Logger,
    level: int,
    message: str,
    user_id: Optional[int] = None,
    correlation_id: Optional[str] = None,
    **extra_fields
) -> None:
    """
    Log a message with additional context.

    Args:
        logger: Logger instance
        level: Log level (logging.DEBUG, INFO, WARNING, ERROR, CRITICAL)
        message: Log message
        user_id: Optional user ID for user-specific operations
        correlation_id: Optional correlation ID (uses context if not provided)
        **extra_fields: Additional fields to include in structured logs

    Example:
        log_with_context(
            logger, logging.INFO, "Message sent",
            user_id=12345,
            mood_category="MOTIVATION",
            message_frequency=3
        )
    """
    extra = {}

    if user_id is not None:
        extra['user_id'] = user_id

    if correlation_id is not None:
        extra['correlation_id'] = correlation_id
    elif correlation_id_var.get() is not None:
        extra['correlation_id'] = correlation_id_var.get()

    if extra_fields:
        extra['extra_fields'] = extra_fields

    logger.log(level, message, extra=extra)
