"""Centralized logging configuration for Git MCP Server."""

import logging
import os
import sys
import threading
from pathlib import Path
from typing import Optional, Union

from rich.console import Console
from rich.logging import RichHandler
from rich.traceback import install


class LoggingConfig:
    """Centralized logging configuration singleton with thread-safe initialization."""

    _instance: Optional["LoggingConfig"] = None
    _initialized = False
    _lock = threading.Lock()

    def __new__(cls) -> "LoggingConfig":
        if cls._instance is None:
            with cls._lock:
                # Double-checked locking pattern for thread safety
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.console = Console()
        self.debug_enabled = False
        self.log_file: Optional[Path] = None
        self.log_level = logging.INFO
        self._setup_from_env()
        self._initialized = True

    def _setup_from_env(self):
        """Setup logging configuration from environment variables."""
        # Check for debug environment variables
        debug_env = os.getenv("GIT_MCP_SERVER_DEBUG", "").lower()
        self.debug_enabled = debug_env in ("1", "true", "yes", "on")

        # Check log level from environment
        log_level_env = os.getenv("GIT_MCP_SERVER_LOG_LEVEL", "").upper()
        if log_level_env:
            try:
                self.log_level = getattr(logging, log_level_env)
                if log_level_env == "DEBUG":
                    self.debug_enabled = True
            except AttributeError:
                # Invalid log level, warn user and keep default
                # Use print since logging isn't configured yet
                print(
                    f"Warning: Invalid log level '{log_level_env}', using INFO",
                    file=sys.stderr,
                )

        # Set up log file if specified
        log_file_env = os.getenv("GIT_MCP_SERVER_LOG_FILE")
        if log_file_env:
            self.log_file = Path(log_file_env).expanduser()
            # Create log directory if needed
            self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def enable_debug(self):
        """Enable debug logging."""
        self.debug_enabled = True
        self.log_level = logging.DEBUG

    def configure_logging(self, logger_name: str = "git_mcp") -> logging.Logger:
        """Configure and return a logger instance."""
        logger = logging.getLogger(logger_name)
        logger.setLevel(self.log_level)

        # Only clear handlers if they exist to avoid affecting other loggers
        if logger.handlers:
            logger.handlers.clear()

        # Console handler with Rich formatting
        console_handler = RichHandler(
            console=self.console,
            show_time=self.debug_enabled,
            show_path=self.debug_enabled,
            rich_tracebacks=True,
            tracebacks_show_locals=self.debug_enabled,
        )
        console_handler.setLevel(self.log_level)

        # Set format based on debug mode
        if self.debug_enabled:
            formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
        else:
            formatter = logging.Formatter("%(message)s")

        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # File handler if log file is specified
        if self.log_file:
            file_handler = logging.FileHandler(self.log_file, mode="a")
            file_handler.setLevel(self.log_level)
            file_formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)

        # Install rich traceback handler for better error display
        if self.debug_enabled:
            install(console=self.console, show_locals=True)

        return logger


def get_logger(name: str = "git_mcp") -> logging.Logger:
    """Get a configured logger instance."""
    config = LoggingConfig()
    return config.configure_logging(name)


def setup_logging(
    debug: bool = False, log_file: Optional[Union[str, Path]] = None
) -> LoggingConfig:
    """Setup logging configuration.

    Args:
        debug: Enable debug mode (overrides environment variables)
        log_file: Path to log file (overrides environment variables)

    Returns:
        LoggingConfig instance for further configuration if needed

    Note:
        Priority order: Function arguments > Environment variables > Defaults
    """
    config = LoggingConfig()

    # CLI arguments have highest priority
    if debug:
        config.enable_debug()

    if log_file:
        config.log_file = Path(log_file).expanduser()
        config.log_file.parent.mkdir(parents=True, exist_ok=True)

    return config
