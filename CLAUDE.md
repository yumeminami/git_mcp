# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Git MCP Server is a Model Context Protocol (MCP) server that enables issue-to-code automation for Claude Code, Gemini CLI, and Codex. It provides unified Git platform access for GitLab and GitHub (including GitHub Enterprise) through MCP tools and slash commands for complete development workflows.

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
uv run ruff format git_mcp/
uv run bandit -r git_mcp/
uv run mypy git_mcp/ --ignore-missing-imports --no-strict-optional

# Run pre-commit hooks manually (includes ruff, bandit, mypy, yaml/json checks)
uv run pre-commit run --all-files

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=git_mcp --cov-report=term-missing

# Run specific test file
uv run pytest tests/test_logging.py

# Test CLI entry points
uv run git-mcp --help
uv run git-mcp-server --help

# Test MCP server directly
echo '{"jsonrpc": "2.0", "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0.0"}}, "id": 1}' | git-mcp-server

# Build distribution packages
uv build

# Run development version in interactive MCP mode
uv run mcp dev git_mcp/mcp_server.py
```

### Installation & Setup
```bash
# Install from PyPI and configure Claude Code integration
uv tool install git_mcp_server
git-mcp-server --install-claude

# Install from PyPI and configure Gemini CLI integration
git-mcp-server --install-gemini

# Install from PyPI and configure Codex integration
git-mcp-server --install-codex

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

**Codex Commands** (`git_mcp/codex_commands/`):
- Markdown-based command definitions for Codex integration
- Installed to `~/.codex/prompts/` during setup
- Same workflow commands adapted for Codex prompt format
- Includes memory integration via `~/.codex/AGENTS.md`

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
5. **Slash Commands**: Update Claude, Gemini, and Codex command definitions when adding new workflows

## File Structure Context

- `git_mcp/` - Main Python package
- `git_mcp/claude_commands/` - Slash commands for Claude Code (.md files)
- `git_mcp/gemini_commands/` - Slash commands for Gemini CLI (.toml files)
- `git_mcp/codex_commands/` - Slash commands for Codex (.md files)
- `git_mcp/commands/` - CLI command implementations
- `git_mcp/platforms/` - Git platform adapters (GitLab, GitHub, etc.)
- `git_mcp/services/` - Service layer for business logic
- `git_mcp/core/` - Core configuration and exception handling
- `git_mcp/utils/` - Utility functions for output formatting and platform detection

## Dependencies

**Python Version**: Requires Python >=3.13 (specified in pyproject.toml)

**Build System**: Uses hatchling as the build backend

Core dependencies (from pyproject.toml):
- `python-gitlab>=4.4.0` - GitLab API client
- `PyGithub>=2.1.0` - GitHub API client
- `mcp[cli]>=1.0.0` - Model Context Protocol implementation
- `click>=8.1.0` - CLI framework
- `rich>=13.0.0` - Rich text and table formatting
- `keyring>=24.0.0` - Secure credential storage
- `pydantic>=2.5.0` - Data validation and settings management
- `httpx>=0.26.0` - HTTP client for async requests
- `gitpython>=3.1.0` - Git repository interaction
- `pyyaml>=6.0.0` - YAML configuration parsing
- `tool>=0.8.0` - Tool utilities
- `pre-commit>=4.2.0` - Git hooks for code quality

Development tools:
- `ruff>=0.1.0` - Linting and code formatting
- `bandit[toml]>=1.7.0` - Security vulnerability scanning
- `pytest>=8.0.0` - Testing framework with comprehensive test suite
- `pytest-asyncio>=0.23.0` - Async testing support
- `pytest-cov>=5.0.0` - Test coverage reporting
- `coverage>=7.0.0` - Coverage measurement
- `mypy>=1.17.1` - Static type checking
- `pip-audit>=2.0.0` - Security vulnerability scanning

**Pre-commit Configuration**: Includes ruff (linting/formatting), bandit (security), mypy (type checking), and standard file checks. Run with `uv run pre-commit run --all-files`.

## API Documentation

**Platform API References:**

### GitHub API (PyGithub)
- **Examples & Usage Patterns**: https://pygithub.readthedocs.io/en/stable/examples.html
  - Comprehensive examples for common GitHub operations
  - Authentication methods and best practices
  - Rate limiting and pagination handling
- **API Reference**: https://pygithub.readthedocs.io/en/stable/github_objects.html
  - Complete class and method documentation
  - Object relationships and property details

### GitLab API (python-gitlab)
- **API Objects Reference**: https://python-gitlab.readthedocs.io/en/stable/api-objects.html
  - Complete list of available API objects and methods
  - CRUD operations for issues, merge requests, projects
  - Advanced features like pipelines, deployments, and wiki management
- **Usage Guide**: https://python-gitlab.readthedocs.io/en/stable/gl_objects/
  - Object-specific documentation with examples
  - Authentication and connection management

**When to Use These Resources:**
- **Customizing platform adapters** (`git_mcp/platforms/`) - Reference API objects and methods
- **Debugging API interactions** - Understand response structures and error handling
- **Extending MCP tools** (`git_mcp/mcp_server.py`) - Add new platform operations
- **Developing slash commands** - Integrate additional API functionality

**Additional Resources:**
- **GitHub REST API Docs**: https://docs.github.com/en/rest
- **GitLab REST API Docs**: https://docs.gitlab.com/ee/api/

## Security Notes

- All access tokens are stored securely in system keyring, never in config files
- Bandit security scanning is configured to skip safe subprocess usage (`B404`, `B603`, `B607`)
- Platform connections are tested before storing configuration
- Username auto-detection reduces manual configuration and potential errors

## MCP Tools Reference

The MCP server exposes approximately 25 tools organized into categories:

**Platform Management**: `list_platforms`, `test_platform_connection`, `refresh_platform_username`, `get_platform_config`, `get_current_user_info`

**Project Operations**: `list_projects`, `get_project_details`, `create_project`, `delete_project`

**Issue Management**: `list_issues`, `list_all_issues`, `list_my_issues`, `get_issue_details`, `get_issue_by_url`, `create_issue`, `update_issue`, `close_issue`

**Merge Requests**: `list_merge_requests`, `get_merge_request_details`, `create_merge_request` (supports GitLab cross-project MRs), `list_my_merge_requests`, `get_merge_request_diff`, `get_merge_request_commits`, `create_issue_comment`

**Repository Operations**: `create_fork`, `get_fork_info`, `list_forks`

All tools support async operations and return structured data for integration with AI assistants.

## GitLab Fork MR Support

**GitLab Cross-Project Merge Requests** are fully supported using the `target_project_id` parameter:

### GitLab Fork MR Usage

```python
# GitLab cross-project MR (from fork to upstream project)
create_merge_request(
    platform="gitlab",
    project_id="456",              # fork project ID (source project)
    source_branch="feature-branch",
    target_branch="main",
    title="Fix issue #123",
    target_project_id="123",       # upstream project ID (target project)
    description="Detailed description..."
)

# GitLab same-project MR (existing functionality unchanged)
create_merge_request(
    platform="gitlab",
    project_id="123",
    source_branch="feature-branch",
    target_branch="main",
    title="Fix issue #123"
)
```

### GitHub Fork PR Comparison

```python
# GitHub cross-repository PR (using branch reference format)
create_merge_request(
    platform="github",
    project_id="upstream-owner/upstream-repo",  # target upstream repository
    source_branch="fork-owner:feature-branch",  # fork branch reference
    target_branch="main",
    title="Fix issue #123"
)
```

**Key Differences**:
- **GitLab**: Uses `target_project_id` parameter to specify target project
- **GitHub**: Uses `owner:branch` format in `source_branch` to specify cross-repository reference
