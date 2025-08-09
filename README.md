# Git MCP Server

A unified command-line tool and **MCP (Model Context Protocol) Server** for managing Git repositories across GitHub and GitLab platforms.

## Features

### Core Functionality
- 🚀 **Multi-Platform Support** - Unified management for GitHub and GitLab platforms
- 🔐 **Secure Authentication** - Uses system keyring for secure token storage
- 📊 **Rich Output** - Support for table, JSON, and YAML output formats
- 🔧 **Project Management** - Create, delete, and list projects
- 🎯 **Issue Tracking** - Complete issue management with comments and full details
- 🚀 **CI/CD Integration** - Manage pipelines and deployments

### MCP Server Integration
- 🤖 **Claude Code Integration** - Works as an MCP server for Claude Code
- 🛠️ **Tool-based Interface** - Expose Git operations as MCP tools
- 📚 **Resource Access** - Provide Git data as MCP resources
- 🔄 **Real-time Operations** - Async support for responsive interactions

## Installation

```bash
# Clone repository
git clone <repository-url>
cd git_mpc

# Install dependencies using uv
uv sync

# Or using pip (requires virtual environment)
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
pip install -e .
```

## Quick Start

### 1. Configure Platforms

```bash
# Add GitLab configuration
uv run git-mcp config add my-gitlab gitlab --url https://gitlab.com

# Add private GitLab instance
uv run git-mcp config add company-gitlab gitlab --url https://git.company.com

# List configured platforms
uv run git-mcp config list

# Test connection
uv run git-mcp config test my-gitlab
```

### 2. Project Management

```bash
# List projects
uv run git-mcp project list --platform my-gitlab

# Get project details
uv run git-mcp project get 123 --platform my-gitlab

# Create new project
uv run git-mcp project create "My New Project" \\
  --platform my-gitlab \\
  --visibility private \\
  --description "Project description"

# Delete project
uv run git-mcp project delete 123 --platform my-gitlab
```

### 3. Issue Management

```bash
# List issues in a project
uv run git-mcp issue list 123 --platform my-gitlab

# Create a new issue
uv run git-mcp issue create 123 "Bug in login system" \\
  --platform my-gitlab \\
  --description "Users cannot login with valid credentials" \\
  --labels "bug,urgent" \\
  --assignee johndoe

# Get issue details with comments
uv run git-mcp issue get 123 45 --platform my-gitlab
# This displays comprehensive issue information including:
# - Basic info (ID, state, dates, author)
# - Labels and milestones
# - Full description
# - All user comments with timestamps and authors

# Update an issue
uv run git-mcp issue update 123 45 \\
  --platform my-gitlab \\
  --state closed \\
  --comment "Fixed in v1.2.0"

# Search issues
uv run git-mcp issue search --project 123 --query "login" --platform my-gitlab
```

### 4. Merge Request Workflow

```bash
# List merge requests in a project
uv run git-mcp mr list --project 123 --platform my-gitlab --state opened

# Create a merge request (auto-detects current branch as source)
uv run git-mcp mr create 123 \\
  --platform my-gitlab \\
  --target main \\
  --title "Implement user authentication" \\
  --description "Added JWT-based authentication system" \\
  --assignee revieweruser \\
  --labels "feature,security"

# Get merge request details
uv run git-mcp mr get 123 45 --platform my-gitlab

# Approve a merge request
uv run git-mcp mr approve 123 45 --platform my-gitlab --comment "LGTM!"

# Merge a merge request
uv run git-mcp mr merge 123 45 \\
  --platform my-gitlab \\
  --should-remove-source-branch \\
  --squash
```

### 5. Output Formats

```bash
# Table format (default)
uv run git-mcp project list --format table

# JSON format
uv run git-mcp --format json project list --platform my-gitlab

# YAML format
uv run git-mcp --format yaml project list --platform my-gitlab
```

## Command Reference

### Global Options

- `--format [table|json|yaml]` - Output format
- `--platform TEXT` - Specify default platform
- `--config-dir PATH` - Configuration directory path

### Configuration Management

```bash
git-mcp config add <name> <type> --url <url>     # Add platform configuration
git-mcp config list                              # List platform configurations
git-mcp config remove <name>                     # Remove platform configuration
git-mcp config test [name]                       # Test platform connection
```

### Project Management

```bash
git-mcp project list [OPTIONS]                   # List projects
git-mcp project get <project_id>                 # Get project details
git-mcp project create <name> [OPTIONS]          # Create project
git-mcp project delete <project_id>              # Delete project
```

### Issue Management

```bash
git-mcp issue list <project_id> [OPTIONS]        # List issues in a project
git-mcp issue get <project_id> <issue_id>        # Get issue details with comments
git-mcp issue create <project_id> <title> [OPTIONS] # Create new issue
git-mcp issue update <project_id> <issue_id> [OPTIONS] # Update issue
git-mcp issue close <project_id> <issue_id>      # Close issue
git-mcp issue search --project <id> --query <text> # Search issues
```

### Merge Request Management

```bash
git-mcp mr list --project <id> [OPTIONS]         # List MRs in a project
git-mcp mr get <project_id> <mr_id>               # Get MR details
git-mcp mr create <project_id> [OPTIONS]         # Create new MR
git-mcp mr update <project_id> <mr_id> [OPTIONS] # Update MR
git-mcp mr approve <project_id> <mr_id>           # Approve MR
git-mcp mr merge <project_id> <mr_id> [OPTIONS]  # Merge MR
git-mcp mr close <project_id> <mr_id>             # Close MR
```

#### Project List Options

- `--visibility [public|internal|private]` - Project visibility
- `--archived [true|false]` - Include archived projects
- `--owned [true|false]` - Only show owned projects
- `--starred [true|false]` - Only show starred projects
- `--search <term>` - Search keyword
- `--limit <number>` - Limit result count

#### Issue Management Options

- `--state [opened|closed|all]` - Filter by issue state
- `--assignee <username>` - Filter by assignee
- `--author <username>` - Filter by author
- `--labels <label1,label2>` - Filter by labels
- `--milestone <name>` - Filter by milestone
- `--search <term>` - Search in title and description
- `--sort [created_asc|created_desc|updated_asc|updated_desc]` - Sort order

#### Merge Request Management Options

**List Options:**

- `--project <id>` - Project scope (required)
- `--state [opened|closed|merged|all]` - Filter by MR state
- `--assignee <username>` - Filter by assignee
- `--author <username>` - Filter by author
- `--source-branch <branch>` - Filter by source branch
- `--target-branch <branch>` - Filter by target branch
- `--labels <label1,label2>` - Filter by labels

**Create Options:**
- `--source <branch>` - Source branch (auto-detected if not specified)
- `--target <branch>` - Target branch (default: main)
- `--draft` - Create as draft MR
- `--remove-source-branch` - Remove source branch when merged
- `--squash` - Squash commits when merging

## Configuration File

Configuration file is located at `~/.git-mcp/config.yaml`:

```yaml
platforms:
  my-gitlab:
    type: gitlab
    url: https://gitlab.com
    username: myuser

  company-gitlab:
    type: gitlab
    url: https://git.company.com

defaults:
  platform: my-gitlab
  output_format: table
  page_size: 20
  timeout: 30

aliases:
  - name: "work"
    platform: company-gitlab
    project: "team/my-project"
```

Tokens are stored securely in the system keyring and not saved in the configuration file.

## Development

### Project Structure

```
git_mpc/
├── core/           # Core functionality
│   ├── config.py   # Configuration management
│   └── exceptions.py # Exception definitions
├── platforms/      # Platform adapters
│   ├── base.py     # Base class definitions
│   └── gitlab.py   # GitLab adapter
├── commands/       # Command handlers
│   └── project.py  # Project management commands
├── utils/          # Utility modules
│   └── output.py   # Output formatting
└── cli.py          # CLI entry point
```

### Adding New Platforms

1. Inherit from `PlatformAdapter` base class
2. Implement all abstract methods
3. Register new platform type in CLI

### Running Tests

```bash
uv run pytest
```

## MCP Server Usage

### Installation and Setup

#### Recommended: Install from PyPI/uv

```bash
# Install via uv (recommended)
uv tool install git_mcp_server

# Or install via pip
pip install git_mcp_server

# Setup Claude Code integration and slash commands
git-mcp-server --install-claude
```

This will:
- Install Git MCP Server globally on your system
- Add MCP server to Claude Code (user scope - available in all projects)
- Install issue-to-code workflow slash commands to `~/.claude/commands/`
- Provide next steps for platform configuration

#### Alternative: Install from Source

For development or latest features:

```bash
# Clone and install from source
git clone <repository-url>
cd git_mcp
uv tool install --from . git_mcp

# Setup Claude Code integration
git-mcp-server --install-claude
```

#### Development Setup

For local development:

```bash
# Clone repository
git clone <repository-url>
cd git_mcp

# Install in development mode
uv sync --all-extras

# Run locally for testing
uv run git-mcp-server

# Install development version globally
uv tool install --from . git_mcp --force
git-mcp-server --install-claude
```

### Running as an MCP Server

```bash
# If installed globally
git-mcp-server

# If running locally
uv run git-mcp-server

# Test interactively during development
uv run mcp dev git_mcp/mcp_server.py
```

### Configuration Features

#### Automatic Username Detection

When adding a new platform, the system will automatically fetch your username from the provided token:

```bash
# Username will be auto-fetched from token
git-mcp config add my-gitlab gitlab --url https://gitlab.com --token YOUR_TOKEN

# Disable auto-fetch if needed
git-mcp config add my-gitlab gitlab --url https://gitlab.com --token YOUR_TOKEN --no-auto-username

# Refresh username for existing platform
git-mcp config refresh-username my-gitlab
```

**Supported Platforms for Auto-fetch:**
- ✅ GitLab (gitlab.com and private instances)
- 🚧 GitHub (planned)

### MCP Scopes Explained

- **Local scope** (`-s local`): Only available in the current project directory
- **User scope** (`-s user`): Available across all projects for the current user
- **Project scope** (`-s project`): Shared via `.mcp.json` file in the project

For most users, **user scope with global installation** is recommended.

### Available MCP Tools

When running as an MCP server, the following tools are available:

#### Platform Management
- `list_platforms()` - List all configured Git platforms
- `test_platform_connection(platform)` - Test connection to a platform
- `refresh_platform_username(platform)` - Refresh username by fetching from token
- `get_platform_config(platform)` - Get configuration info for a platform (including username)
- `get_current_user_info(platform)` - Get current user info directly from platform API

#### Project Operations
- `list_projects(platform, limit=20)` - List projects from a platform
- `get_project_details(platform, project_id)` - Get detailed project information

#### Issue Management
- `list_issues(platform, project_id, state='opened', limit=20)` - List issues in a project
- `get_issue_details(platform, project_id, issue_id)` - Get issue details with comments
- `create_issue(platform, project_id, title, description?, labels?, assignee?)` - Create new issue

#### Merge Request Operations
- `list_merge_requests(platform, project_id, state='opened', limit=20)` - List merge requests

#### Resources
- `config://platforms` - Get current platform configuration
- `project://{platform}/{project_id}` - Get project information as a resource

### Issue-to-Code Workflow

After installation, use these slash commands in Claude Code for complete issue-driven development:

```bash
# Workflow Option 1: Start with my issues dashboard
/issue                                              # List my assigned issues
# (select an issue from the list)
/issue https://gitlab.com/group/project/-/issues/123  # Analyze selected issue
/plan                                               # Generate dev plan
/implement                                         # Write code
/test                                             # Generate tests
/doc                                             # Update documentation
/pr 123                                         # Create PR/MR & close issue

# Workflow Option 2: Direct issue analysis
/issue https://gitlab.com/group/project/-/issues/456  # Analyze specific issue
/plan                                                 # Generate dev plan
# ... continue with implement/test/doc/pr
```

**Available Commands:**
- `/issue` - List my assigned issues (no args) or analyze specific issue (with args)
- `/plan` - Generate development plans based on issue analysis
- `/implement` - Implement planned functionality with best practices
- `/test` - Generate comprehensive test suites
- `/doc` - Update documentation and API docs
- `/pr` - Create pull/merge requests with automatic issue closing

### MCP Integration Examples

```python
# Example: Using the MCP tools through Claude Code
# These operations will be available when the server is configured

# List all configured platforms
platforms = list_platforms()

# Get projects from a specific platform
projects = list_projects("my-gitlab", limit=10)

# Create a new issue
new_issue = create_issue(
    platform="my-gitlab",
    project_id="123",
    title="Bug in login system",
    description="Users cannot login with valid credentials",
    labels=["bug", "urgent"]
)
```

### Troubleshooting

#### Verify Installation

```bash
# Check if globally installed
which git-mcp-server
git-mcp-server --help

# Check Claude Code configuration
claude mcp list

# Test MCP connection
echo '{"jsonrpc": "2.0", "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0.0"}}, "id": 1}' | git-mcp-server
```

#### Common Issues

1. **"Command not found" after global installation**
   ```bash
   # Reinstall with uv tool
   uv tool uninstall git_mcp
   uv tool install --from /path/to/git_mcp git_mcp
   ```

2. **MCP server not working in different directories**
   - Make sure you used `-s user` scope for global availability
   - Use global installation instead of local project paths

3. **Configuration issues**
   ```bash
   # First configure a platform
   git-mcp config add my-gitlab gitlab --url https://gitlab.com

   # Then test the MCP tools
   ```

#### Update Global Installation

```bash
# Update to latest version
cd /path/to/git_mcp
git pull
uv tool install --from . git_mcp --force
```

## Supported Platforms

- ✅ **GitLab** - Full support (GitLab.com and private instances)
- 🚧 **GitHub** - Planned support

## Contributing

Issues and Pull Requests are welcome!

## License

MIT License
