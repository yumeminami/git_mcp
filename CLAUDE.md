# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Git MCP Server is a Model Context Protocol (MCP) server that enables issue-to-code automation for Claude Code and Gemini CLI. It provides unified Git platform access for GitLab and GitHub (including GitHub Enterprise) through MCP tools and slash commands for complete development workflows.

## Key Commands

### Development & Testing
```bash
# Install from source (development)
uv sync --all-extras
uv run git-mcp-server

# Install globally for testing
uv tool install --from . git_mcp_server --force

# Run linting and security checks
uv run ruff check git_mcp/
uv run bandit -r git_mcp/

# Run pre-commit hooks manually
uv run pre-commit run --all-files

# Run tests (when implemented - uses placeholder test currently)
uv run pytest

# Test CLI entry points
uv run git-mcp --help
uv run git-mcp-server --help
```

### Installation & Setup
```bash
# Install from PyPI and configure Claude Code integration
uv tool install git_mcp_server
git-mcp-server --install-claude

# Install from PyPI and configure Gemini CLI integration
git-mcp-server --install-gemini

# Local development installation
./install.sh
```

### Configuration Management
```bash
# Add platform configuration
git-mcp config add my-gitlab gitlab --url https://gitlab.com
git-mcp config add my-github github --url https://github.com

# Test platform connections
git-mcp config test my-gitlab
git-mcp config test my-github

# List configured platforms
git-mcp config list

# Refresh username from token
git-mcp config refresh-username my-gitlab
```

## Architecture

### Core Components

**MCP Server** (`git_mcp/mcp_server.py`):
- Main MCP interface with ~25 tools for platform management, issues, projects, and merge requests
- Supports automatic Claude Code and Gemini CLI integration with `--install-claude` and `--install-gemini` flags
- Resources for platform configuration and project data

**CLI Interface** (`git_mcp/cli.py`):
- Click-based CLI with commands for config, project, issue, and MR management
- Global context management with configurable output formats (table, json, yaml)
- Async command execution with proper error handling

**Configuration System** (`git_mcp/core/config.py`):
- YAML-based config storage at `~/.git-mcp/config.yaml`
- Secure keyring-based token storage
- Automatic username fetching from platform APIs
- Platform, defaults, and aliases management

**Platform Adapters** (`git_mcp/platforms/`):
- Base adapter interface (`base.py`) with common Git platform operations
- GitLab implementation (`gitlab.py`) with full API coverage
- GitHub implementation (`github.py`) with full API coverage including GitHub Enterprise
- Extensible design for additional platforms

**Service Layer** (`git_mcp/services/platform_service.py`):
- Unified service interface abstracting platform-specific implementations
- Handles platform routing, error handling, and data normalization
- Async operations with proper exception management

### Slash Commands Integration

**Claude Code Commands** (`git_mcp/claude_commands/`):
- Complete issue-to-code workflow: `/issue` → `/plan` → `/implement` → `/test` → `/doc` → `/pr`
- Installed to `~/.claude/commands/` during setup
- Markdown-based command definitions with MCP tool integration

**Gemini CLI Commands** (`git_mcp/gemini_commands/`):
- TOML-based command definitions for Gemini CLI
- Installed to `~/.gemini/commands/` during setup
- Same workflow commands adapted for Gemini CLI format

### Key Design Patterns

- **Async-first**: All platform operations are async for better performance
- **Service abstraction**: Platform operations go through unified service layer
- **Configuration management**: Centralized config with secure token storage
- **Error handling**: Comprehensive exception handling with user-friendly messages
- **Extensibility**: Plugin-style architecture for adding new platforms

## Development Workflow

When working on this codebase:

1. **Configuration Changes**: Modify `git_mcp/core/config.py` for new config options
2. **Platform Support**: Add new adapters in `git_mcp/platforms/` following the base interface
3. **MCP Tools**: Add new tools in `git_mcp/mcp_server.py` with proper async patterns
4. **CLI Commands**: Extend commands in `git_mcp/commands/` using Click framework
5. **Slash Commands**: Update both Claude and Gemini command definitions when adding new workflows

## File Structure Context

- `git_mcp/` - Main Python package
- `git_mcp/claude_commands/` - Slash commands for Claude Code (.md files)
- `git_mcp/gemini_commands/` - Slash commands for Gemini CLI (.toml files)
- `git_mcp/commands/` - CLI command implementations
- `git_mcp/platforms/` - Git platform adapters (GitLab, GitHub, etc.)
- `git_mcp/services/` - Service layer for business logic
- `git_mcp/core/` - Core configuration and exception handling
- `git_mcp/utils/` - Utility functions for output formatting and platform detection

## Dependencies

Core dependencies (from pyproject.toml):
- `python-gitlab>=4.4.0` - GitLab API client
- `PyGithub>=2.1.0` - GitHub API client
- `mcp[cli]>=1.0.0` - Model Context Protocol implementation
- `click>=8.1.0` - CLI framework
- `rich>=13.0.0` - Rich text and table formatting
- `keyring>=24.0.0` - Secure credential storage
- `pydantic>=2.5.0` - Data validation and settings management

Development tools:
- `ruff>=0.1.0` - Linting and code formatting
- `bandit[toml]>=1.7.0` - Security vulnerability scanning
- `pytest>=8.0.0` - Testing framework (configured, tests not yet implemented)
- `pytest-asyncio>=0.23.0` - Async testing support
- `pre-commit>=4.2.0` - Git hooks for code quality
- `pip-audit>=2.0.0` - Security vulnerability scanning

## Security Notes

- All access tokens are stored securely in system keyring, never in config files
- Bandit security scanning is configured to skip safe subprocess usage (`B404`, `B603`, `B607`)
- Platform connections are tested before storing configuration
- Username auto-detection reduces manual configuration and potential errors
