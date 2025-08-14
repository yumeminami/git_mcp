"""Logging configuration for git-mcp."""

import logging
import os
import sys
from pathlib import Path
from typing import Optional, Union
from rich.console import Console
from rich.logging import RichHandler
from rich.text import Text


class LoggingConfig:
    """Centralized logging configuration for git-mcp."""
    
    _instance: Optional["LoggingConfig"] = None
    _initialized: bool = False
    
    def __new__(cls) -> "LoggingConfig":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.console = Console(stderr=True)
            self.logger = logging.getLogger("git_mcp")
            self._setup_logging()
            LoggingConfig._initialized = True
    
    def _setup_logging(self) -> None:
        """Setup logging configuration based on environment and defaults."""
        # Get log level from environment or default to INFO
        log_level_str = os.getenv("GIT_MCP_SERVER_LOG_LEVEL", "INFO").upper()
        
        try:
            log_level = getattr(logging, log_level_str)
        except AttributeError:
            log_level = logging.INFO
            self.console.print(
                f"[yellow]Warning: Invalid log level '{log_level_str}', using INFO[/yellow]"
            )
        
        # Check if debug mode is enabled
        debug_enabled = (
            os.getenv("GIT_MCP_SERVER_DEBUG", "false").lower() in ("true", "1", "yes") or
            log_level_str == "DEBUG"
        )
        
        if debug_enabled:
            log_level = logging.DEBUG
        
        # Configure the root logger
        self.logger.setLevel(log_level)
        
        # Remove any existing handlers
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Setup console handler with rich formatting
        rich_handler = RichHandler(
            console=self.console,
            show_time=True,
            show_path=debug_enabled,
            markup=True,
            rich_tracebacks=True,
            show_level=True,
        )
        rich_handler.setLevel(log_level)
        
        # Create formatter
        formatter = logging.Formatter(
            "%(name)s: %(message)s",
            datefmt="[%X]"
        )
        rich_handler.setFormatter(formatter)
        
        self.logger.addHandler(rich_handler)
        
        # Setup file handler if configured
        log_file = os.getenv("GIT_MCP_SERVER_LOG_FILE")
        if log_file:
            self._setup_file_handler(log_file, log_level)
        
        # Prevent propagation to avoid duplicate messages
        self.logger.propagate = False
        
        # Log initial configuration
        if debug_enabled:
            self.logger.debug(f"Logging initialized - Level: {logging.getLevelName(log_level)}")
            self.logger.debug(f"Log file: {log_file if log_file else 'None (console only)'}")
    
    def _setup_file_handler(self, log_file: str, log_level: int) -> None:
        """Setup file logging handler."""
        try:
            log_path = Path(log_file).expanduser()
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(log_path, mode='a')
            file_handler.setLevel(log_level)
            
            file_formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            file_handler.setFormatter(file_formatter)
            
            self.logger.addHandler(file_handler)
            self.logger.debug(f"File logging enabled: {log_path}")
            
        except Exception as e:
            self.console.print(
                f"[yellow]Warning: Failed to setup file logging: {e}[/yellow]"
            )
    
    def enable_debug(self) -> None:
        """Enable debug logging programmatically."""
        self.logger.setLevel(logging.DEBUG)
        for handler in self.logger.handlers:
            handler.setLevel(logging.DEBUG)
            if isinstance(handler, RichHandler):
                handler._log_render.show_path = True
        self.logger.debug("Debug logging enabled programmatically")
    
    def get_logger(self, name: Optional[str] = None) -> logging.Logger:
        """Get a logger instance."""
        if name:
            return logging.getLogger(f"git_mcp.{name}")
        return self.logger


# Global logging configuration instance
_logging_config: Optional[LoggingConfig] = None


def setup_logging(debug: bool = False, log_file: Optional[Union[str, Path]] = None) -> LoggingConfig:
    """Setup logging configuration.
    
    Args:
        debug: Enable debug logging
        log_file: Optional path to log file
    
    Returns:
        LoggingConfig instance
    """
    global _logging_config
    
    # Set environment variables if provided
    if debug:
        os.environ["GIT_MCP_SERVER_LOG_LEVEL"] = "DEBUG"
        os.environ["GIT_MCP_SERVER_DEBUG"] = "true"
    
    if log_file:
        os.environ["GIT_MCP_SERVER_LOG_FILE"] = str(log_file)
    
    if _logging_config is None:
        _logging_config = LoggingConfig()
    elif debug:
        # If debug was enabled after initialization, update configuration
        _logging_config.enable_debug()
    
    return _logging_config


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get a logger instance.
    
    Args:
        name: Optional logger name (will be prefixed with 'git_mcp.')
    
    Returns:
        Logger instance
    """
    if _logging_config is None:
        setup_logging()
    
    return _logging_config.get_logger(name)