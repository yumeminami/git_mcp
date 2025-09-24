# Git MCP Server

**A Model Context Protocol (MCP) server for Claude Code, Gemini CLI, and Codex** that enables complete issue-to-code automation across GitHub and GitLab platforms.

## 🚀 What is Git MCP Server?

Git MCP Server transforms your development workflow by connecting AI assistants directly to your Git repositories. It provides:

- **🤖 MCP Integration**: Full support for Claude Code, Gemini CLI, and Codex via Model Context Protocol
- **📋 Issue-to-Code Workflow**: Complete automation from issue analysis to PR creation
- **🎯 Slash Commands**: Pre-built workflow commands (`/issue`, `/plan`, `/implement`, `/test`, `/doc`, `/pr`)
- **🔧 Multi-Platform**: Unified interface for GitLab and GitHub
- **🔐 Secure**: Keyring-based token storage with auto-username detection

## 🎯 Issue-to-Code Workflow

Transform how you handle development tasks with these automated slash commands:

```bash
# 1. Analyze any issue from URL
/issue https://gitlab.com/group/project/-/issues/123

# 2. Generate development plan
/plan

# 3. Implement the solution
/implement

# 4. Create comprehensive tests
/test

# 5. Update documentation
/doc

# 6. Create PR/MR and close issue
/pr 123
```

**That's it!** From issue analysis to pull request in 6 commands.

## 📦 Installation

### Quick Setup (Recommended)

**For Claude Code:**
```bash
# Install from PyPI
uv tool install git_mcp_server

# Setup Claude Code integration (adds MCP server + slash commands)
git-mcp-server --install-claude
```

**For Gemini CLI:**
```bash
# Install from PyPI
uv tool install git_mcp_server

# Setup Gemini CLI integration (adds MCP server + slash commands)
git-mcp-server --install-gemini
```

**For Codex:**
```bash
# Install from PyPI
uv tool install git_mcp_server

# Setup Codex integration (adds MCP server + slash commands)
git-mcp-server --install-codex
```

This automatically:
- ✅ Installs Git MCP Server globally
- ✅ Configures MCP server in Claude Code/Gemini CLI/Codex
- ✅ Installs slash commands to respective directories
- ✅ Adds code memory guidelines (Codex: AGENTS.md)
- ✅ Provides setup instructions

### Alternative Installation

```bash
# Using pip
pip install git_mcp_server
git-mcp-server --install-claude  # or --install-gemini or --install-codex

# From source (development)
git clone <repository-url>
cd git_mcp
uv tool install --from . git_mcp_server
git-mcp-server --install-claude  # or --install-gemini or --install-codex
```

## ⚡ Quick Start

### 1. Configure Your Git Platform

```bash
# Add GitLab (public or private instance)
git-mcp config add my-gitlab gitlab --url https://gitlab.com

# Add GitHub (public or GitHub Enterprise)
git-mcp config add my-github github --url https://github.com

# Test the connections
git-mcp config test my-gitlab
git-mcp config test my-github
```

The system will automatically:
- 🔐 Prompt for your access token
- 👤 Fetch your username automatically
- 💾 Store credentials securely in system keyring

### 2. Start Using Slash Commands

In Claude Code, Gemini CLI, or Codex, you can now use:

#### **`/issue`** - Smart Issue Analysis
```bash
# List your assigned issues
/issue

# Analyze specific issue from any GitLab/GitHub URL
/issue https://gitlab.com/group/project/-/issues/123
```

#### **`/plan`** - Generate Development Plans
```bash
# Create structured implementation plan based on issue analysis
/plan
```

#### **`/implement`** - Code Implementation
```bash
# Implement the planned solution with best practices
/implement
```

#### **`/test`** - Test Generation
```bash
# Generate comprehensive test suites
/test
```

#### **`/doc`** - Documentation Updates
```bash
# Update documentation and API docs
/doc
```

#### **`/pr`** - Create Pull Requests
```bash
# Create PR/MR and automatically close related issue
/pr 123
```

## 🛠️ Available MCP Tools

When configured, Claude Code, Gemini CLI, and Codex gain access to these powerful tools:

### Platform Management
- `list_platforms()` - List configured Git platforms
- `test_platform_connection(platform)` - Test platform connectivity
- `get_platform_config(platform)` - Get platform configuration
- `refresh_platform_username(platform)` - Update username from token

### Issue Operations
- `list_my_issues(platform)` - List issues assigned to you
- `get_issue_by_url(url)` - Analyze issues from GitLab/GitHub URLs
- `get_issue_details(platform, project_id, issue_id)` - Get detailed issue info
- `create_issue(platform, project_id, title, ...)` - Create new issues

### Project Management
- `list_projects(platform)` - List accessible projects
- `get_project_details(platform, project_id)` - Get project information

### Merge Requests
- `list_merge_requests(platform, project_id)` - List merge requests
- `create_merge_request(platform, project_id, ...)` - Create pull/merge requests

## 🎛️ Configuration

### Platform Configuration

Git MCP Server stores configuration in `~/.git-mcp/config.yaml`:

```yaml
platforms:
  my-gitlab:
    type: gitlab
    url: https://gitlab.com
    username: myuser  # Auto-fetched from token

  company-gitlab:
    type: gitlab
    url: https://git.company.com
    username: myuser

defaults:
  platform: my-gitlab
```

**Security Note**: Access tokens are stored securely in your system keyring, not in config files.

### Automatic Username Detection

```bash
# Username automatically fetched from token
git-mcp config add my-gitlab gitlab --url https://gitlab.com

# Refresh username for existing platforms
git-mcp config refresh-username my-gitlab
```

## 🔧 Advanced Usage

### Running MCP Server Directly

```bash
# Start MCP server (for debugging)
git-mcp-server

# Interactive development mode
uv run mcp dev git_mcp/mcp_server.py
```

### MCP Scope Configuration

**Claude Code:**
- **User scope** (recommended): Available across all Claude Code projects
- **Local scope**: Only in current project directory
- **Project scope**: Shared via `.mcp.json` in project

**Gemini CLI:**
- **Global settings**: Configured in `~/.gemini/settings.json`
- **Project settings**: Can override in project-specific settings
- **Commands**: Located in `~/.gemini/commands/` (global) or `.gemini/commands/` (project)

**Codex:**
- **Global configuration**: MCP server configured in `~/.codex/config.toml`
- **Commands**: Located in `~/.codex/prompts/` directory
- **Memory integration**: Code guidelines in `~/.codex/AGENTS.md`

### Development Setup

```bash
# Clone repository
git clone <repository-url>
cd git_mcp

# Install in development mode
uv sync --all-extras

# Run locally
uv run git-mcp-server

# Install development version globally
uv tool install --from . git_mcp_server --force
```

## 📚 Workflow Examples

### Complete Feature Development

```bash
# Start with your assigned issues
/issue

# Select and analyze specific issue
/issue https://gitlab.com/team/project/-/issues/456

# Generate implementation plan
/plan

# Implement with best practices
/implement

# Create comprehensive tests
/test

# Update documentation
/doc

# Create PR and close issue
/pr 456
```

### Bug Fix Workflow

```bash
# Analyze bug report
/issue https://gitlab.com/team/project/-/issues/789

# Plan the fix
/plan

# Implement fix
/implement

# Add regression tests
/test

# Update docs if needed
/doc

# Submit fix
/pr 789
```

## 🔍 Troubleshooting

### Verify Installation

```bash
# Check global installation
which git-mcp-server
git-mcp-server --help

# Verify Claude Code integration
claude mcp list

# Verify Gemini CLI integration
gemini /mcp

# Verify Codex integration
ls ~/.codex/prompts/  # Should show slash commands
cat ~/.codex/config.toml  # Should show git-mcp-server

# Test MCP connection
echo '{"jsonrpc": "2.0", "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0.0"}}, "id": 1}' | git-mcp-server
```

### Common Issues

**"No MCP servers configured"**
```bash
# Reinstall MCP integration
git-mcp-server --install-claude  # or --install-gemini
```

**"Command not found" after installation**
```bash
# Reinstall with uv
uv tool uninstall git_mcp_server
uv tool install git_mcp_server
```

**Slash commands not working**
```bash
# Check commands directory (Claude Code)
ls ~/.claude/commands/

# Check commands directory (Gemini CLI)
ls ~/.gemini/commands/

# Check commands directory (Codex)
ls ~/.codex/prompts/

# Reinstall if missing
git-mcp-server --install-claude  # or --install-gemini or --install-codex
```

### Update to Latest Version

```bash
# Update package
uv tool install git_mcp_server --upgrade

# Reinstall integration
git-mcp-server --install-claude  # or --install-gemini
```

## 🐛 Debug & Logging

Git MCP Server includes comprehensive debugging and logging capabilities to help troubleshoot issues and understand system behavior.

### Debug Mode

Enable debug mode to get detailed logging output with enhanced formatting:

**CLI Commands:**
```bash
# Enable debug mode for CLI commands
git-mcp --debug config list
git-mcp --debug issue list --platform github

# Debug mode shows detailed operation logs
git-mcp --debug config test my-gitlab
```

**MCP Server:**
```bash
# Start MCP server with debug logging
git-mcp-server --debug

# Shows detailed MCP tool calls and responses
git-mcp-server --debug
```

### Environment Variables

Configure logging behavior using environment variables:

```bash
# Set log level (DEBUG, INFO, WARNING, ERROR)
export GIT_MCP_SERVER_LOG_LEVEL=DEBUG

# Enable debug mode (alternative to --debug flag)
export GIT_MCP_SERVER_DEBUG=true

# Log to file instead of/in addition to console
export GIT_MCP_SERVER_LOG_FILE=~/.git-mcp/debug.log

# Run with environment variables
git-mcp-server
```

### Log File Configuration

Enable file logging for persistent debugging:

```bash
# Set log file path
export GIT_MCP_SERVER_LOG_FILE=~/.git-mcp/git-mcp.log

# Logs will be appended to file with timestamps
git-mcp-server --debug
```

**Log file format:**
```
2025-08-15 02:05:23,123 - git_mcp.mcp_server - DEBUG - MCP Tool: list_platforms called
2025-08-15 02:05:23,124 - git_mcp.platforms.gitlab - DEBUG - Connecting to GitLab at https://gitlab.com
2025-08-15 02:05:23,156 - git_mcp.mcp_server - DEBUG - MCP Tool: list_platforms returned 2 platforms
```

### Rich Console Output

Debug mode enables rich console formatting with:

- **🎨 Colored output** for different log levels
- **📁 File paths** shown for debug messages
- **⏰ Timestamps** for all debug entries
- **📊 Structured tracebacks** for errors
- **🔍 Local variables** in error traces (debug mode only)

### Troubleshooting Common Issues

**Enable debug mode when experiencing:**

```bash
# Connection issues
export GIT_MCP_SERVER_LOG_LEVEL=DEBUG
git-mcp config test my-gitlab

# MCP tool failures
git-mcp-server --debug

# Authentication problems
export GIT_MCP_SERVER_DEBUG=true
git-mcp issue list --platform github
```

**Debug MCP Integration:**

```bash
# Test MCP server communication
echo '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}' | git-mcp-server --debug

# Claude Code MCP debugging
claude mcp logs git-mcp-server

# Check MCP server status
claude mcp status
```

### Log Levels Explained

- **DEBUG**: Detailed function calls, API requests, internal operations
- **INFO**: General information about operations and status
- **WARNING**: Non-critical issues that may need attention
- **ERROR**: Critical errors that prevent operation

### Environment Variable Priority

Configuration priority (highest to lowest):
1. **CLI flags**: `--debug` overrides environment variables
2. **Environment variables**: `GIT_MCP_SERVER_*` settings
3. **Default values**: INFO level, console output only

### Debug Examples

**Debugging Platform Connection:**
```bash
# Enable debug and test connection
export GIT_MCP_SERVER_LOG_LEVEL=DEBUG
git-mcp config test my-gitlab

# Output shows detailed connection process:
# DEBUG - Connecting to GitLab at https://gitlab.com
# DEBUG - Authentication successful for user: myusername
# DEBUG - API version: v4
# INFO - Connection to 'my-gitlab' successful
```

**Debugging MCP Tool Calls:**
```bash
# Start server with debug logging
git-mcp-server --debug

# Shows MCP tool invocations:
# DEBUG - MCP Tool: list_projects called with platform='gitlab'
# DEBUG - Found 15 projects for user
# DEBUG - MCP Tool: list_projects returned 15 projects
```

**File + Console Logging:**
```bash
# Log to both console and file
export GIT_MCP_SERVER_LOG_LEVEL=DEBUG
export GIT_MCP_SERVER_LOG_FILE=~/.git-mcp/debug.log

# Console shows rich formatted output
# File contains timestamped plain text logs
git-mcp-server
```

This logging system helps diagnose issues, understand system behavior, and provides detailed insights for development and troubleshooting.

## 🌟 Key Benefits

- **⚡ Speed**: From issue to PR in minutes, not hours
- **🎯 Focus**: AI handles boilerplate, you focus on logic
- **📋 Consistency**: Standardized workflow across all projects
- **🔧 Flexibility**: Works with any GitLab instance
- **🤖 Intelligence**: AI assistants understand your codebase context
- **🔐 Security**: Secure credential management

## 🛣️ Supported Platforms

- ✅ **GitLab** - Full support (gitlab.com and private instances)
- ✅ **GitHub** - Full support (github.com and GitHub Enterprise)

## 🤝 Contributing

Issues and Pull Requests welcome! This project enables powerful AI-assisted development workflows.

## 📄 License

MIT License

---

**Ready to supercharge your development workflow?**

```bash
# For Claude Code
uv tool install git_mcp_server && git-mcp-server --install-claude

# For Gemini CLI
uv tool install git_mcp_server && git-mcp-server --install-gemini

# For Codex
uv tool install git_mcp_server && git-mcp-server --install-codex
```

Then try `/issue` in your AI assistant! 🚀
