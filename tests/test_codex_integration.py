"""Tests for Codex integration functionality."""

import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

from git_mcp.mcp_server import (
    install_codex_integration,
    _configure_codex_mcp_server,
    _install_codex_commands,
    _update_codex_agents_memory,
    _validate_config_path,
)


class TestValidateConfigPath:
    """Test configuration path validation for security."""

    def test_valid_codex_path(self):
        """Test that valid Codex paths are accepted."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Mock home directory
            with patch("pathlib.Path.home") as mock_home:
                mock_home.return_value = Path(tmp_dir)

                # Test valid path
                test_path = Path(tmp_dir) / ".codex" / "config.toml"
                result = _validate_config_path(test_path)

                assert result == test_path.resolve()

    def test_valid_claude_path(self):
        """Test that valid Claude paths are accepted."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            with patch("pathlib.Path.home") as mock_home:
                mock_home.return_value = Path(tmp_dir)

                test_path = Path(tmp_dir) / ".claude" / "commands" / "issue.md"
                result = _validate_config_path(test_path)

                assert result == test_path.resolve()

    def test_invalid_directory_rejected(self):
        """Test that paths outside allowed directories are rejected."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            with patch("pathlib.Path.home") as mock_home:
                mock_home.return_value = Path(tmp_dir)

                # Test invalid directory
                test_path = Path(tmp_dir) / ".malicious" / "config.toml"

                with pytest.raises(ValueError, match="not in allowed directories"):
                    _validate_config_path(test_path)

    def test_path_outside_home_rejected(self):
        """Test that paths outside home directory are rejected."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            with patch("pathlib.Path.home") as mock_home:
                mock_home.return_value = Path(tmp_dir) / "home"

                # Test path outside home
                test_path = "/etc/passwd"

                with pytest.raises(ValueError, match="not under user home directory"):
                    _validate_config_path(test_path)

    def test_path_traversal_attack_prevented(self):
        """Test that path traversal attacks are prevented."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            with patch("pathlib.Path.home") as mock_home:
                mock_home.return_value = Path(tmp_dir)

                # Test path traversal attempt
                test_path = Path(tmp_dir) / ".codex" / ".." / ".." / "etc" / "passwd"

                with pytest.raises(ValueError, match="not under user home directory"):
                    _validate_config_path(test_path)

    def test_custom_allowed_dirs(self):
        """Test validation with custom allowed directories."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            with patch("pathlib.Path.home") as mock_home:
                mock_home.return_value = Path(tmp_dir)

                # Test with custom allowed dirs
                test_path = Path(tmp_dir) / ".custom" / "config.toml"
                result = _validate_config_path(test_path, allowed_dirs=[".custom"])

                assert result == test_path.resolve()

                # Test rejection of default dirs when custom specified
                test_path2 = Path(tmp_dir) / ".codex" / "config.toml"
                with pytest.raises(ValueError, match="not in allowed directories"):
                    _validate_config_path(test_path2, allowed_dirs=[".custom"])


class TestCodexMCPServerConfiguration:
    """Test MCP server configuration for Codex."""

    def setup_method(self):
        """Setup for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = Path(self.temp_dir) / ".codex" / "config.toml"

    def teardown_method(self):
        """Cleanup after each test."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_configure_new_config(self):
        """Test configuring MCP server with new config file."""
        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = Path(self.temp_dir)

            # Mock TOML imports
            with patch("git_mcp.mcp_server.tomllib") as mock_tomllib:
                with patch("git_mcp.mcp_server.tomli_w") as mock_tomli_w:
                    mock_tomllib.loads.return_value = {}
                    mock_tomli_w.dumps.return_value = '[mcp_servers]\n[mcp_servers.git-mcp-server]\ncommand = "git-mcp-server"\nargs = []\nenv = {}\n'

                    result = _configure_codex_mcp_server()

                    assert result is True
                    mock_tomli_w.dumps.assert_called_once()

    def test_configure_existing_config(self):
        """Test configuring MCP server with existing config file."""
        # Create existing config file
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        self.config_file.write_text('[other_section]\nkey = "value"')

        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = Path(self.temp_dir)

            with patch("git_mcp.mcp_server.tomllib") as mock_tomllib:
                with patch("git_mcp.mcp_server.tomli_w") as mock_tomli_w:
                    # Mock existing config
                    mock_tomllib.loads.return_value = {
                        "other_section": {"key": "value"}
                    }
                    mock_tomli_w.dumps.return_value = "config_content"

                    result = _configure_codex_mcp_server()

                    assert result is True
                    # Verify existing config was loaded
                    mock_tomllib.loads.assert_called_once()

    def test_configure_toml_decode_error(self):
        """Test handling of TOML decode errors."""
        # Create malformed config file
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        self.config_file.write_text("invalid toml [[[")

        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = Path(self.temp_dir)

            with patch("git_mcp.mcp_server.tomllib") as mock_tomllib:
                with patch("git_mcp.mcp_server.tomli_w"):
                    # Mock TOML decode error
                    mock_tomllib.loads.side_effect = Exception("Invalid TOML")

                    with patch("builtins.print") as mock_print:
                        result = _configure_codex_mcp_server()

                        assert result is False
                        mock_print.assert_called()

    def test_configure_permission_error(self):
        """Test handling of permission errors."""
        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = Path(self.temp_dir)

            with patch("git_mcp.mcp_server.tomllib") as mock_tomllib:
                with patch("git_mcp.mcp_server.tomli_w"):
                    mock_tomllib.loads.return_value = {}
                    # Mock permission error on write
                    mock_path = MagicMock()
                    mock_path.write_text.side_effect = PermissionError("Access denied")

                    with patch(
                        "git_mcp.mcp_server._validate_config_path",
                        return_value=mock_path,
                    ):
                        with patch("builtins.print") as mock_print:
                            result = _configure_codex_mcp_server()

                            assert result is False
                            mock_print.assert_called()

    def test_configure_missing_tomli_import(self):
        """Test handling of missing tomli import."""
        with patch("git_mcp.mcp_server.tomllib", side_effect=ImportError):
            with patch("git_mcp.mcp_server.tomli", side_effect=ImportError):
                with patch("builtins.print") as mock_print:
                    result = _configure_codex_mcp_server()

                    assert result is False
                    mock_print.assert_called_with(
                        "❌ TOML support not available. Please install tomli: pip install tomli"
                    )

    def test_configure_missing_tomli_w_import(self):
        """Test handling of missing tomli-w import."""
        with patch("git_mcp.mcp_server.tomli_w", side_effect=ImportError):
            with patch("builtins.print") as mock_print:
                result = _configure_codex_mcp_server()

                assert result is False
                mock_print.assert_called_with(
                    "❌ TOML writing support not available. Please install tomli-w: pip install tomli-w"
                )


class TestCodexCommandsInstallation:
    """Test slash commands installation for Codex."""

    def setup_method(self):
        """Setup for each test."""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Cleanup after each test."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_install_commands_success(self):
        """Test successful installation of Codex commands."""
        commands_dir = Path(self.temp_dir) / ".codex" / "prompts"

        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = Path(self.temp_dir)

            # Mock importlib.resources
            with patch("importlib.resources.files") as mock_files:
                mock_ref = MagicMock()
                mock_files.return_value = mock_ref

                # Mock command files
                mock_files_list = [
                    MagicMock(name="issue.md", suffix=".md"),
                    MagicMock(name="plan.md", suffix=".md"),
                    MagicMock(name="implement.md", suffix=".md"),
                ]
                mock_ref.iterdir.return_value = mock_files_list

                # Mock file reading
                for mock_file in mock_files_list:
                    mock_file.read_text.return_value = "# Command content"

                result = _install_codex_commands()

                assert result is True
                # Verify directory was created
                assert commands_dir.exists()

    def test_install_commands_no_files_found(self):
        """Test handling when no command files are found."""
        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = Path(self.temp_dir)

            with patch("importlib.resources.files") as mock_files:
                mock_ref = MagicMock()
                mock_files.return_value = mock_ref
                # No .md files found
                mock_ref.iterdir.return_value = []

                with patch("builtins.print") as mock_print:
                    result = _install_codex_commands()

                    assert result is False
                    mock_print.assert_called()

    def test_install_commands_package_not_found(self):
        """Test handling when command package is not found."""
        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = Path(self.temp_dir)

            with patch("importlib.resources.files", side_effect=FileNotFoundError):
                with patch("builtins.print") as mock_print:
                    result = _install_codex_commands()

                    assert result is False
                    mock_print.assert_called()

    def test_install_commands_path_validation_error(self):
        """Test handling of path validation errors."""
        with patch(
            "git_mcp.mcp_server._validate_config_path",
            side_effect=ValueError("Invalid path"),
        ):
            with patch("builtins.print") as mock_print:
                result = _install_codex_commands()

                assert result is False
                mock_print.assert_called()


class TestCodexAgentsMemoryUpdate:
    """Test AGENTS.md memory file updates."""

    def setup_method(self):
        """Setup for each test."""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Cleanup after each test."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_update_agents_memory_success(self):
        """Test successful update of AGENTS.md."""
        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = Path(self.temp_dir)

            with patch(
                "git_mcp.mcp_server._append_code_memory_to_file", return_value=True
            ):
                with patch("builtins.print") as mock_print:
                    result = _update_codex_agents_memory()

                    assert result is True
                    mock_print.assert_called()

    def test_update_agents_memory_failure(self):
        """Test handling of AGENTS.md update failure."""
        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = Path(self.temp_dir)

            with patch(
                "git_mcp.mcp_server._append_code_memory_to_file", return_value=False
            ):
                with patch("builtins.print") as mock_print:
                    result = _update_codex_agents_memory()

                    assert result is False
                    mock_print.assert_called()


class TestCodexIntegrationMain:
    """Test main Codex integration function."""

    def test_install_codex_integration_success(self):
        """Test successful Codex integration installation."""
        with patch("shutil.which", return_value="/usr/bin/codex"):
            with patch(
                "git_mcp.mcp_server._configure_codex_mcp_server", return_value=True
            ):
                with patch(
                    "git_mcp.mcp_server._install_codex_commands", return_value=True
                ):
                    with patch(
                        "git_mcp.mcp_server._update_codex_agents_memory",
                        return_value=True,
                    ):
                        with patch("builtins.print") as mock_print:
                            install_codex_integration()

                            # Verify success messages
                            mock_print.assert_called()

    def test_install_codex_integration_codex_not_found(self):
        """Test Codex integration when Codex CLI is not found."""
        with patch("shutil.which", return_value=None):
            with patch(
                "git_mcp.mcp_server._configure_codex_mcp_server", return_value=True
            ):
                with patch(
                    "git_mcp.mcp_server._install_codex_commands", return_value=True
                ):
                    with patch(
                        "git_mcp.mcp_server._update_codex_agents_memory",
                        return_value=True,
                    ):
                        with patch("builtins.print") as mock_print:
                            install_codex_integration()

                            # Should warn but continue
                            assert mock_print.called

    def test_install_codex_integration_config_failure(self):
        """Test handling of configuration failure."""
        with patch("shutil.which", return_value="/usr/bin/codex"):
            with patch(
                "git_mcp.mcp_server._configure_codex_mcp_server", return_value=False
            ):
                with patch("builtins.print") as mock_print:
                    install_codex_integration()

                    # Should print error message
                    mock_print.assert_called()

    def test_install_codex_integration_commands_failure(self):
        """Test handling of commands installation failure."""
        with patch("shutil.which", return_value="/usr/bin/codex"):
            with patch(
                "git_mcp.mcp_server._configure_codex_mcp_server", return_value=True
            ):
                with patch(
                    "git_mcp.mcp_server._install_codex_commands", return_value=False
                ):
                    with patch("builtins.print") as mock_print:
                        install_codex_integration()

                        # Should print error message
                        mock_print.assert_called()

    def test_install_codex_integration_memory_failure(self):
        """Test handling of memory update failure."""
        with patch("shutil.which", return_value="/usr/bin/codex"):
            with patch(
                "git_mcp.mcp_server._configure_codex_mcp_server", return_value=True
            ):
                with patch(
                    "git_mcp.mcp_server._install_codex_commands", return_value=True
                ):
                    with patch(
                        "git_mcp.mcp_server._update_codex_agents_memory",
                        return_value=False,
                    ):
                        with patch("builtins.print") as mock_print:
                            install_codex_integration()

                            # Should warn about memory update failure
                            mock_print.assert_called()


class TestCodexIntegrationEdgeCases:
    """Test edge cases and error conditions."""

    def test_unicode_handling(self):
        """Test proper Unicode handling in configuration files."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            with patch("pathlib.Path.home") as mock_home:
                mock_home.return_value = Path(tmp_dir)

                # Create config with Unicode content
                config_file = Path(tmp_dir) / ".codex" / "config.toml"
                config_file.parent.mkdir(parents=True, exist_ok=True)
                config_file.write_text('[test]\nkey = "测试"', encoding="utf-8")

                with patch("git_mcp.mcp_server.tomllib") as mock_tomllib:
                    with patch("git_mcp.mcp_server.tomli_w") as mock_tomli_w:
                        mock_tomllib.loads.return_value = {"test": {"key": "测试"}}
                        mock_tomli_w.dumps.return_value = "config"

                        result = _configure_codex_mcp_server()

                        assert result is True

    def test_concurrent_access_safety(self):
        """Test that functions handle concurrent access safely."""
        import threading
        import time

        results = []

        def run_config():
            with patch("pathlib.Path.home") as mock_home:
                mock_home.return_value = Path("/tmp/test_concurrent")

                with patch("git_mcp.mcp_server.tomllib") as mock_tomllib:
                    with patch("git_mcp.mcp_server.tomli_w") as mock_tomli_w:
                        mock_tomllib.loads.return_value = {}
                        mock_tomli_w.dumps.return_value = "config"

                        # Add small delay to simulate concurrent access
                        time.sleep(0.01)
                        results.append(_configure_codex_mcp_server())

        # Run multiple threads
        threads = [threading.Thread(target=run_config) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All should succeed
        assert all(results)
        assert len(results) == 5

    def test_disk_space_handling(self):
        """Test handling of disk space issues."""
        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = Path("/tmp/test")

            with patch("git_mcp.mcp_server.tomllib") as mock_tomllib:
                with patch("git_mcp.mcp_server.tomli_w"):
                    mock_tomllib.loads.return_value = {}

                    # Mock OSError for disk space
                    mock_path = MagicMock()
                    mock_path.write_text.side_effect = OSError(
                        "No space left on device"
                    )

                    with patch(
                        "git_mcp.mcp_server._validate_config_path",
                        return_value=mock_path,
                    ):
                        with patch("builtins.print") as mock_print:
                            result = _configure_codex_mcp_server()

                            assert result is False
                            mock_print.assert_called()
