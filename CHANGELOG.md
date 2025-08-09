# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.5] - 2025-08-09

### Changed
- **Enhanced Command Documentation**: Improved Claude Code and Gemini CLI slash commands with explicit git_mcp_server tool usage hints
  - Updated all command descriptions to mention "using git_mcp_server tools"
  - Added `allowed-tools: mcp__git-mcp-server__*` specifications to Claude commands
  - Included specific tool function hints (e.g., `list_my_issues()`, `get_project_details()`, `create_merge_request()`)
  - Enhanced workflow guidance with concrete MCP tool examples
- **CLAUDE.md Improvements**: Updated development documentation with current testing status and additional dependencies
  - Clarified testing setup status (configured but not yet implemented)
  - Added missing development dependencies (`pytest-asyncio`, `pre-commit`, `pip-audit`)
  - Added pre-commit manual execution command
  - Added CLI entry point testing commands

### Technical
- All slash commands now provide explicit guidance on leveraging available MCP tools
- Improved developer experience with clearer tool usage patterns
- Better integration hints for both Claude Code and Gemini CLI workflows

## [0.1.4] - 2025-08-09

### Added
- **GitHub Support**: Complete GitHub platform integration using PyGithub
  - Full feature parity with GitLab including issues, pull requests, repositories
  - Support for GitHub Enterprise Server
  - MCP server integration for GitHub operations
  - CLI commands for GitHub repository management

### Changed
- **Enhanced CLI**: Fixed merge request creation bug with proper variable scoping
- **Pre-commit Integration**: Added comprehensive code quality hooks
  - Ruff linting and formatting
  - Bandit security scanning
  - MyPy type checking
  - Basic file validation hooks

### Fixed
- Variable scoping issue in CLI merge request creation (`nonlocal source_branch`)
- MyPy type annotation issues in GitHub platform adapter
- Code formatting and linting issues across codebase

### Technical
- Added PyGithub>=2.1.0 dependency for GitHub API access
- Added pre-commit>=4.2.0 for development workflow
- Improved error handling and exception management
- Enhanced platform adapter architecture for multi-platform support

## [0.1.3] - 2024-08-09

### Fixed
- **PyPI Packaging**: Fixed duplicate filename error in wheel distribution
  - Removed redundant `force-include` directive causing file duplication
  - Clean package structure now properly distributes command files
- **Gemini CLI Commands**: Fixed slash command format for proper recognition
  - Changed from `[command]` + `system` to root-level `prompt` field
  - Commands now use `{{args}}` placeholder for argument handling
  - All slash commands (`/issue`, `/plan`, `/implement`, `/test`, `/doc`, `/pr`) now work correctly

### Technical
- Updated all Gemini CLI TOML files to use correct format specification
- Improved package build configuration for cleaner distribution

## [0.1.2] - 2024-08-09

### Added
- **Gemini CLI Support**: Full integration with Google Gemini CLI
  - Added `--install-gemini` flag for easy setup
  - Created TOML-format slash commands for Gemini CLI workflow
  - Automatic MCP server configuration in `~/.gemini/settings.json`
- **Separate Command Files**: Replaced embedded commands with maintainable package files
  - Claude Code commands in `git_mcp/claude_commands/` (.md format)
  - Gemini CLI commands in `git_mcp/gemini_commands/` (.toml format)
  - Proper package structure with `__init__.py` files

### Changed
- **Improved Maintainability**: Removed 600+ lines of embedded command definitions
- **Better Package Structure**: Commands now loaded from package resources via `importlib.resources`
- **Enhanced Documentation**: Updated README with comprehensive Gemini CLI integration guide
- **Installation Process**: Both Claude Code and Gemini CLI now use package-based command installation

### Fixed
- **Package Installation Warning**: Eliminated "Slash commands not found in package" warning
- **Command File Distribution**: Commands now properly included in PyPI package via `pyproject.toml`
- **MCP Server Reinstallation**: Allow seamless reinstallation without manual cleanup

### Technical Details
- Updated `pyproject.toml` with `force-include` for command directories
- Refactored installation functions to use `importlib.resources`
- Added proper error handling for package resource loading
- Improved code quality with linter fixes and formatting

## [0.1.1] - 2024-08-08

### Added
- **Claude Code Integration**: Complete MCP server integration with Claude Code
- **Issue-to-Code Workflow**: Six-step automated development process
  - `/issue` - Smart issue analysis from GitLab/GitHub URLs
  - `/plan` - Development plan generation
  - `/implement` - Code implementation with best practices
  - `/test` - Comprehensive test suite generation
  - `/doc` - Documentation updates
  - `/pr` - Pull/merge request creation
- **MCP Server**: FastMCP-based server with comprehensive Git platform tools
- **Platform Support**: Full GitLab integration (github.com and private instances)

### Features
- **Secure Credentials**: Keyring-based token storage
- **Auto-Username Detection**: Automatic username fetching from access tokens
- **Multi-Platform Ready**: Unified interface for multiple Git platforms
- **CI/CD Integration**: GitHub Actions workflow for automated testing and releases

### Initial Release
- Python 3.13+ support
- Rich CLI interface with colored output
- Comprehensive error handling and logging
- PyPI distribution with automated releases
