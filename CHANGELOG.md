# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.2] - 2025-09-25

### Added
- **Codex Integration**: Complete Codex support for issue-to-code workflow automation
  - Added `--install-codex` flag for seamless Codex setup and configuration
  - Created comprehensive Codex command definitions in `git_mcp/codex_commands/` (.md format)
  - Automatic MCP server configuration in Codex settings
  - AGENTS.md memory integration for enhanced AI assistance context
  - Full workflow support: `/issue`, `/plan`, `/implement`, `/test`, `/doc`, `/pr` commands
  - Closes issue #40

### Improved
- **Code Quality**: Enhanced Codex integration implementation with security improvements
  - Improved code quality and security in Codex command definitions
  - Better error handling and configuration management
  - Enhanced documentation and user experience for Codex workflow

### Technical
- **Package Structure**: Added Codex command files to package distribution
- **Installation Process**: Extended MCP server integration to support Codex alongside Claude Code and Gemini CLI
- **Configuration Management**: Enhanced platform configuration system for multi-client support

## [0.2.1] - 2025-09-20

### Added
- **Code Memory Guidelines**: Added code memory integration to installation process (issue #38)
  - Enhanced installation process with code memory context for better AI assistance
  - Automatic guidance for Claude Code integration during setup

### Fixed
- **Code Memory Content**: Updated and refined code memory content for better accuracy
- **Unused Statement Cleanup**: Removed unused statements to improve code quality

### Technical
- **Installation Enhancement**: Improved post-installation experience with code memory setup
- **Code Quality**: Minor code cleanup and optimization improvements

## [0.2.0] - 2025-08-16

### Added
- **Release Automation**: Complete `/release` command for automated version management
  - Automated version updates in pyproject.toml and __init__.py
  - Changelog generation from git commits
  - Git tag creation and push to remote
  - Comprehensive pre-flight validation and error handling
  - Closes issue #33
- **Issue Comment Functionality**: Full support for issue comment management
  - New MCP tools for creating, reading, and managing issue comments
  - Cross-platform support for both GitLab and GitHub
  - Rich comment threading and metadata support

### Added - Workflow Enhancements
- **Claude Code Review Workflow**: Streamlined code review process integration
- **Claude PR Assistant Workflow**: Enhanced pull request assistance automation
- **Environment Variable Setup**: Automatic environment variable prompts after config add
  - Improves user experience by suggesting required environment variables
  - Reduces configuration errors and setup time

### Added - Debug & Logging
- **Comprehensive Debug System**: Advanced logging capabilities with multiple output levels
  - `--debug` flag for detailed operation tracing
  - Environment variable controls (GIT_MCP_DEBUG, GIT_MCP_LOG_LEVEL)
  - Structured logging with timestamps and component identification
  - Extensive test coverage for logging functionality

### Improved - Documentation
- **Debug & Logging Documentation**: Comprehensive guide for troubleshooting
  - Step-by-step debugging instructions for common issues
  - Environment variable reference and configuration examples
  - Integration examples for various development scenarios

### Fixed
- **CI/CD Workflow**: Removed coverage dependencies from CI workflow
  - Eliminated build failures related to coverage tool dependencies
  - Streamlined CI process for better reliability
- **PR Creation Documentation**: Updated PR creation process documentation
  - Clarified workflow steps and command usage
  - Enhanced examples and troubleshooting guidance

### Technical
- **Pre-commit Updates**: Updated Ruff version in pre-commit configuration
- **Test Infrastructure**: Enhanced test formatting and logging output
- **Development Workflow**: Improved development and testing processes

## [0.1.9] - 2025-08-13

### Added
- **MR/PR Detail Functionality**: Comprehensive merge request and pull request analysis tools
  - **New MCP Tool**: `get_merge_request_diff()` - Retrieves file changes and diff content with configurable options
  - **New MCP Tool**: `get_merge_request_commits()` - Gets commit history with comprehensive metadata including SHA, message, author, dates, statistics, and URLs
  - **Cross-Platform Support**: Both tools work consistently across GitLab and GitHub with standardized response formats
  - **Rich Options**: Configurable diff content inclusion, format selection, and filtering capabilities
  - **Production Features**: Binary file detection, Unicode content support, proper error handling, and performance optimizations
  - **Comprehensive Testing**: Validated on real-world scenarios including large MRs (17 files, 31 commits) and complex merges
  - Implementation spans: `PlatformAdapter` base class, `PlatformService` layer, GitLab/GitHub adapters, and MCP server registration
  - Closes issue #19

## [0.1.8] - 2025-08-11

### Fixed
- **PR Command Issue URL Format**: Updated `/pr` slash command template to use full issue URLs instead of `#xx` format
  - Modified `git_mcp/claude_commands/pr.md` to include instructions for extracting issue URLs from `.claude/issue-*.md` files
  - Added bash command guidance: `grep "URL:" .claude/issue-$ARGUMENTS-*.md | head -1 | cut -d' ' -f2`
  - Maintains backward compatibility while enabling full issue URL usage in PR descriptions
  - Fixes issue #11 where PR descriptions used shorthand `#xx` instead of full issue URLs
- **GitLab & GitHub MR/PR Description Bug**: Enhanced description parameter handling in both GitLab and GitHub merge/pull request creation
  - Added explicit description parameter extraction to ensure it's properly passed to platform APIs
  - Added comprehensive debug logging to track parameter flow through MCP → Service → Adapter layers
  - Fixed MCP server to handle description from both direct parameter and kwargs JSON
  - Fixes issue #6 where descriptions were not appearing in GitLab merge requests and GitHub pull requests

## [0.1.7] - 2025-08-10

### Fixed
- **Critical GitLab MR Creation Bug**: Fixed parameter order mismatch in platform service
  - Platform service was passing `title` before `source_branch` to adapters
  - This caused "source_branch is invalid" errors as title was used as branch name
  - Corrected parameter order to: `project_id, source_branch, target_branch, title`
  - Fixes issue #4

### Improved
- **Branch Validation**: Added branch existence verification before creating merge requests
- **Debug Logging**: Enhanced debug output for merge request creation troubleshooting

## [0.1.6] - 2025-08-10

### Fixed
- **GitLab Merge Request Creation**: Fixed "source_branch is invalid" error by properly handling assignee parameter conversion
  - GitLab adapter now correctly converts `assignee_username` to `assignee_id` as required by GitLab API
  - Added username lookup with graceful error handling for invalid usernames
  - GitHub adapter now properly supports `assignee_username` parameter in merge request creation
  - Both platforms now correctly handle assignee assignment during merge request creation

### Improved
- **Error Handling**: Enhanced platform adapter error handling with better logging and graceful degradation
- **API Compatibility**: Improved GitLab and GitHub API parameter mapping for consistent merge request functionality

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
