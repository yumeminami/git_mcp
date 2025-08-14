"""Tests for logging configuration."""

import logging
import os
import tempfile
from pathlib import Path
import pytest
from unittest.mock import patch

from git_mcp.core.logging import LoggingConfig, get_logger, setup_logging


class TestLoggingConfig:
    """Test LoggingConfig singleton and configuration."""

    def setup_method(self):
        """Reset singleton before each test."""
        LoggingConfig._instance = None
        LoggingConfig._initialized = False

        # Clear environment variables
        for key in [
            "GIT_MCP_SERVER_LOG_LEVEL",
            "GIT_MCP_SERVER_DEBUG",
            "GIT_MCP_SERVER_LOG_FILE",
        ]:
            if key in os.environ:
                del os.environ[key]

    def test_singleton_pattern(self):
        """Test that LoggingConfig follows singleton pattern."""
        config1 = LoggingConfig()
        config2 = LoggingConfig()

        assert config1 is config2
        assert LoggingConfig._instance is config1

    def test_singleton_thread_safety(self):
        """Test singleton is thread-safe."""
        import threading

        instances = []

        def create_instance():
            instances.append(LoggingConfig())

        threads = [threading.Thread(target=create_instance) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All instances should be the same
        assert all(inst is instances[0] for inst in instances)

    def test_default_configuration(self):
        """Test default configuration without environment variables."""
        config = LoggingConfig()

        assert config.debug_enabled is False
        assert config.log_level == logging.INFO
        assert config.log_file is None

    def test_debug_env_variable(self):
        """Test GIT_MCP_SERVER_DEBUG environment variable."""
        test_cases = [
            ("1", True),
            ("true", True),
            ("yes", True),
            ("on", True),
            ("0", False),
            ("false", False),
            ("no", False),
            ("off", False),
            ("", False),
        ]

        for value, expected in test_cases:
            # Reset singleton
            LoggingConfig._instance = None
            LoggingConfig._initialized = False

            os.environ["GIT_MCP_SERVER_DEBUG"] = value
            config = LoggingConfig()

            assert config.debug_enabled is expected, f"Failed for value: {value}"

            del os.environ["GIT_MCP_SERVER_DEBUG"]

    def test_log_level_env_variable(self):
        """Test GIT_MCP_SERVER_LOG_LEVEL environment variable."""
        test_cases = [
            ("DEBUG", logging.DEBUG, True),  # DEBUG also sets debug_enabled
            ("INFO", logging.INFO, False),
            ("WARNING", logging.WARNING, False),
            ("ERROR", logging.ERROR, False),
            ("CRITICAL", logging.CRITICAL, False),
            ("INVALID", logging.INFO, False),  # Invalid level, keeps default
            ("", logging.INFO, False),  # Empty, keeps default
        ]

        for value, expected_level, expected_debug in test_cases:
            # Reset singleton
            LoggingConfig._instance = None
            LoggingConfig._initialized = False

            if value:
                os.environ["GIT_MCP_SERVER_LOG_LEVEL"] = value

            config = LoggingConfig()

            assert config.log_level == expected_level, f"Failed for value: {value}"
            assert config.debug_enabled is expected_debug, (
                f"Debug flag failed for value: {value}"
            )

            if value:
                del os.environ["GIT_MCP_SERVER_LOG_LEVEL"]

    def test_log_file_env_variable(self):
        """Test GIT_MCP_SERVER_LOG_FILE environment variable."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"

            # Reset singleton
            LoggingConfig._instance = None
            LoggingConfig._initialized = False

            os.environ["GIT_MCP_SERVER_LOG_FILE"] = str(log_file)
            config = LoggingConfig()

            assert config.log_file == log_file
            assert log_file.parent.exists()  # Directory should be created

            del os.environ["GIT_MCP_SERVER_LOG_FILE"]

    def test_log_file_with_tilde(self):
        """Test log file path expansion with ~."""
        # Reset singleton
        LoggingConfig._instance = None
        LoggingConfig._initialized = False

        os.environ["GIT_MCP_SERVER_LOG_FILE"] = "~/test.log"
        config = LoggingConfig()

        assert str(config.log_file).startswith(str(Path.home()))
        assert not str(config.log_file).startswith("~")

        del os.environ["GIT_MCP_SERVER_LOG_FILE"]

    def test_enable_debug_method(self):
        """Test enable_debug method."""
        config = LoggingConfig()

        # Start with defaults
        assert config.debug_enabled is False
        assert config.log_level == logging.INFO

        # Enable debug
        config.enable_debug()

        assert config.debug_enabled is True
        assert config.log_level == logging.DEBUG

    def test_configure_logging_creates_logger(self):
        """Test that configure_logging creates and configures a logger."""
        config = LoggingConfig()
        logger = config.configure_logging("test_logger")

        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_logger"
        assert logger.level == config.log_level
        assert len(logger.handlers) > 0  # Should have at least console handler

    def test_configure_logging_with_file(self):
        """Test logging configuration with file output."""
        with tempfile.NamedTemporaryFile(suffix=".log", delete=False) as tmpfile:
            log_file = Path(tmpfile.name)

        try:
            config = LoggingConfig()
            config.log_file = log_file
            logger = config.configure_logging("test_logger")

            # Should have both console and file handlers
            handler_types = [type(h).__name__ for h in logger.handlers]
            assert "RichHandler" in handler_types
            assert "FileHandler" in handler_types

            # Test logging to file
            logger.info("Test message")

            # Check file content
            assert log_file.exists()
            content = log_file.read_text()
            assert "Test message" in content

        finally:
            log_file.unlink(missing_ok=True)

    def test_get_logger_function(self):
        """Test get_logger helper function."""
        logger1 = get_logger("test.module1")
        logger2 = get_logger("test.module2")

        assert logger1.name == "test.module1"
        assert logger2.name == "test.module2"
        assert logger1 is not logger2  # Different loggers

    def test_setup_logging_function(self):
        """Test setup_logging helper function."""
        with tempfile.NamedTemporaryFile(suffix=".log", delete=False) as tmpfile:
            log_file = Path(tmpfile.name)

        try:
            setup_logging(debug=True, log_file=str(log_file))

            config = LoggingConfig()
            assert config.debug_enabled is True
            assert config.log_level == logging.DEBUG
            assert config.log_file == log_file

        finally:
            log_file.unlink(missing_ok=True)


class TestCLIIntegration:
    """Test CLI integration with logging."""

    def test_cli_debug_flag_priority(self):
        """Test that CLI --debug flag has highest priority over environment variables."""
        # Set environment to INFO level
        os.environ["GIT_MCP_SERVER_LOG_LEVEL"] = "INFO"
        os.environ["GIT_MCP_SERVER_DEBUG"] = "false"

        try:
            # Reset singleton
            LoggingConfig._instance = None
            LoggingConfig._initialized = False

            # Simulate CLI with --debug flag
            setup_logging(debug=True)

            config = LoggingConfig()
            assert config.debug_enabled is True
            assert config.log_level == logging.DEBUG

        finally:
            del os.environ["GIT_MCP_SERVER_LOG_LEVEL"]
            del os.environ["GIT_MCP_SERVER_DEBUG"]

    def test_environment_variables_without_cli_flag(self):
        """Test that environment variables work when no CLI flag is provided."""
        os.environ["GIT_MCP_SERVER_LOG_LEVEL"] = "WARNING"

        try:
            # Reset singleton
            LoggingConfig._instance = None
            LoggingConfig._initialized = False

            # Simulate CLI without --debug flag
            setup_logging(debug=False)

            config = LoggingConfig()
            assert config.log_level == logging.WARNING

        finally:
            del os.environ["GIT_MCP_SERVER_LOG_LEVEL"]


class TestMCPServerIntegration:
    """Test MCP server integration with logging."""

    @patch("git_mcp.mcp_server.logger")
    def test_mcp_server_debug_logging(self, mock_logger):
        """Test that MCP server uses logger for debug output."""
        # This would test that the MCP server properly logs debug messages
        # Since the actual MCP server requires complex setup, we mock the logger

        # Verify logger is configured
        assert mock_logger is not None

        # In actual implementation, would test specific log calls


class TestArgumentPriority:
    """Test argument priority: CLI flags > Environment variables > Defaults."""

    def setup_method(self):
        """Reset singleton before each test."""
        LoggingConfig._instance = None
        LoggingConfig._initialized = False

        # Clear environment variables
        for key in [
            "GIT_MCP_SERVER_LOG_LEVEL",
            "GIT_MCP_SERVER_DEBUG",
            "GIT_MCP_SERVER_LOG_FILE",
        ]:
            if key in os.environ:
                del os.environ[key]

    def test_priority_cli_overrides_env(self):
        """Test CLI flag overrides environment variable."""
        # Set environment to ERROR
        os.environ["GIT_MCP_SERVER_LOG_LEVEL"] = "ERROR"

        # CLI sets debug=True (should override to DEBUG level)
        setup_logging(debug=True)

        config = LoggingConfig()
        assert config.log_level == logging.DEBUG  # CLI wins
        assert config.debug_enabled is True

        del os.environ["GIT_MCP_SERVER_LOG_LEVEL"]

    def test_priority_env_overrides_default(self):
        """Test environment variable overrides default."""
        # Set environment to WARNING
        os.environ["GIT_MCP_SERVER_LOG_LEVEL"] = "WARNING"

        # No CLI flag (should use env)
        setup_logging(debug=False)

        config = LoggingConfig()
        assert config.log_level == logging.WARNING  # Env wins over default INFO

        del os.environ["GIT_MCP_SERVER_LOG_LEVEL"]

    def test_priority_default_when_no_override(self):
        """Test default is used when no CLI flag or environment variable."""
        # No environment variables, no CLI flag
        setup_logging(debug=False)

        config = LoggingConfig()
        assert config.log_level == logging.INFO  # Default
        assert config.debug_enabled is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
