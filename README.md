# Git MPC (Multi-Platform Controller)

A unified command-line tool for managing Git repositories across multiple platforms including GitLab, GitHub, and Bitbucket.

## Features

- 🚀 **Multi-Platform Support** - Unified management for GitLab, GitHub, and other platforms
- 🔐 **Secure Authentication** - Uses system keyring for secure token storage
- 📊 **Rich Output** - Support for table, JSON, and YAML output formats
- 🔧 **Project Management** - Create, delete, and list projects
- 🎯 **Issue Tracking** - Manage issues and merge requests
- 🚀 **CI/CD Integration** - Manage pipelines and deployments

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
uv run git-mpc config add my-gitlab gitlab --url https://gitlab.com

# Add private GitLab instance
uv run git-mpc config add company-gitlab gitlab --url https://git.company.com

# List configured platforms
uv run git-mpc config list

# Test connection
uv run git-mpc config test my-gitlab
```

### 2. Project Management

```bash
# List projects
uv run git-mpc project list --platform my-gitlab

# Get project details
uv run git-mpc project get 123 --platform my-gitlab

# Create new project
uv run git-mpc project create "My New Project" \\
  --platform my-gitlab \\
  --visibility private \\
  --description "Project description"

# Delete project
uv run git-mpc project delete 123 --platform my-gitlab
```

### 3. Issue Management

```bash
# List issues in a project
uv run git-mpc issue list 123 --platform my-gitlab

# Create a new issue
uv run git-mpc issue create 123 "Bug in login system" \\
  --platform my-gitlab \\
  --description "Users cannot login with valid credentials" \\
  --labels "bug,urgent" \\
  --assignee johndoe

# Get issue details
uv run git-mpc issue get 123 45 --platform my-gitlab

# Update an issue
uv run git-mpc issue update 123 45 \\
  --platform my-gitlab \\
  --state closed \\
  --comment "Fixed in v1.2.0"

# Search issues
uv run git-mpc issue search --project 123 --query "login" --platform my-gitlab
```

### 4. Output Formats

```bash
# Table format (default)
uv run git-mpc project list --format table

# JSON format
uv run git-mpc --format json project list --platform my-gitlab

# YAML format
uv run git-mpc --format yaml project list --platform my-gitlab
```

## Command Reference

### Global Options

- `--format [table|json|yaml]` - Output format
- `--platform TEXT` - Specify default platform
- `--config-dir PATH` - Configuration directory path

### Configuration Management

```bash
git-mpc config add <name> <type> --url <url>     # Add platform configuration
git-mpc config list                              # List platform configurations
git-mpc config remove <name>                     # Remove platform configuration
git-mpc config test [name]                       # Test platform connection
```

### Project Management

```bash
git-mpc project list [OPTIONS]                   # List projects
git-mpc project get <project_id>                 # Get project details
git-mpc project create <name> [OPTIONS]          # Create project
git-mpc project delete <project_id>              # Delete project
```

### Issue Management

```bash
git-mpc issue list <project_id> [OPTIONS]        # List issues in a project
git-mpc issue get <project_id> <issue_id>        # Get issue details
git-mpc issue create <project_id> <title> [OPTIONS] # Create new issue
git-mpc issue update <project_id> <issue_id> [OPTIONS] # Update issue
git-mpc issue close <project_id> <issue_id>      # Close issue
git-mpc issue search --project <id> --query <text> # Search issues
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

## Configuration File

Configuration file is located at `~/.git-mpc/config.yaml`:

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

## Supported Platforms

- ✅ **GitLab** - Full support (GitLab.com and private instances)
- 🚧 **GitHub** - Planned support
- 🚧 **Bitbucket** - Planned support

## Contributing

Issues and Pull Requests are welcome!

## License

MIT License
