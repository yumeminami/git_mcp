"""Git MCP Server - MCP interface for Git repository management."""

from typing import List, Dict, Any, Optional
from mcp.server.fastmcp import FastMCP

from .services.platform_service import PlatformService


# Create the MCP server
mcp = FastMCP("Git MCP Server")


# Platform Management Tools
@mcp.tool()
async def list_platforms() -> List[Dict[str, str]]:
    """List all configured Git platforms (GitLab, GitHub, etc.)"""
    return await PlatformService.list_platforms()


@mcp.tool()
async def test_platform_connection(platform: str) -> Dict[str, Any]:
    """Test connection to a configured platform"""
    return await PlatformService.test_platform_connection(platform)


@mcp.tool()
async def refresh_platform_username(platform: str) -> Dict[str, Any]:
    """Refresh username for a configured platform by fetching from token"""
    return await PlatformService.refresh_platform_username(platform)


@mcp.tool()
async def get_platform_config(platform: str) -> Dict[str, Any]:
    """Get configuration information for a specific platform"""
    return await PlatformService.get_platform_config(platform)


@mcp.tool()
async def get_current_user_info(platform: str) -> Dict[str, Any]:
    """Get current user information directly from platform API"""
    return await PlatformService.get_current_user_info(platform)


# Project Management Tools
@mcp.tool()
async def list_projects(
    platform: str, limit: Optional[int] = 20, **filters
) -> List[Dict[str, Any]]:
    """List projects from a specified Git platform"""
    return await PlatformService.list_projects(platform, limit, **filters)


@mcp.tool()
async def get_project_details(platform: str, project_id: str) -> Dict[str, Any]:
    """Get detailed information about a specific project"""
    return await PlatformService.get_project_details(platform, project_id)


@mcp.tool()
async def create_project(platform: str, name: str, **kwargs) -> Dict[str, Any]:
    """Create a new project on the specified platform"""
    return await PlatformService.create_project(platform, name, **kwargs)


@mcp.tool()
async def delete_project(platform: str, project_id: str) -> Dict[str, Any]:
    """Delete a project from the specified platform"""
    return await PlatformService.delete_project(platform, project_id)


# Issue Management Tools
@mcp.tool()
async def list_issues(
    platform: str,
    project_id: str,
    state: str = "opened",
    limit: Optional[int] = 20,
    **filters,
) -> List[Dict[str, Any]]:
    """List issues in a project. State can be 'opened', 'closed', or 'all'"""
    return await PlatformService.list_issues(
        platform, project_id, state, limit, **filters
    )


@mcp.tool()
async def list_all_issues(
    platform: str,
    state: str = "opened",
    limit: Optional[int] = 20,
    **filters,
) -> List[Dict[str, Any]]:
    """List issues across all projects (global search). No project_id needed."""
    return await PlatformService.list_all_issues(platform, state, limit, **filters)


@mcp.tool()
async def list_my_issues(
    platform: str,
    state: str = "opened",
    limit: Optional[int] = 20,
    **filters,
) -> List[Dict[str, Any]]:
    """List issues assigned to me across all projects."""
    # Add assignee filter automatically using configured username
    try:
        config = await PlatformService.get_platform_config(platform)
        if not config.get("found") or not config.get("username"):
            return [
                {
                    "error": f"No username configured for platform '{platform}'. "
                    f"Use 'refresh_platform_username' tool to fetch it automatically."
                }
            ]

        filters["assignee"] = config["username"]
        return await PlatformService.list_all_issues(platform, state, limit, **filters)
    except Exception as e:
        return [{"error": f"Failed to list my issues: {str(e)}"}]


@mcp.tool()
async def get_issue_details(
    platform: str, project_id: str, issue_id: str
) -> Dict[str, Any]:
    """Get detailed information about a specific issue including comments"""
    return await PlatformService.get_issue_details(platform, project_id, issue_id)


@mcp.tool()
async def get_issue_by_url(url: str) -> Dict[str, Any]:
    """Get issue details by URL. Supports GitLab and GitHub URLs.

    Example URLs:
    - https://gitlab.com/group/project/-/issues/123
    - https://github.com/user/repo/issues/456
    """
    return await PlatformService.get_issue_by_url(url)


@mcp.tool()
async def create_issue(
    platform: str,
    project_id: str,
    title: str,
    description: Optional[str] = None,
    labels: Optional[List[str]] = None,
    assignee: Optional[str] = None,
    **kwargs,
) -> Dict[str, Any]:
    """Create a new issue in a project"""
    return await PlatformService.create_issue(
        platform, project_id, title, description, labels, assignee, **kwargs
    )


@mcp.tool()
async def update_issue(
    platform: str,
    project_id: str,
    issue_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    labels: Optional[List[str]] = None,
    assignee: Optional[str] = None,
    state: Optional[str] = None,
    **kwargs,
) -> Dict[str, Any]:
    """Update an existing issue"""
    update_kwargs = kwargs.copy()
    if title:
        update_kwargs["title"] = title
    if description:
        update_kwargs["description"] = description
    if labels:
        update_kwargs["labels"] = ",".join(labels)
    if assignee:
        update_kwargs["assignee_username"] = assignee
    if state:
        update_kwargs["state_event"] = state

    return await PlatformService.update_issue(
        platform, project_id, issue_id, **update_kwargs
    )


@mcp.tool()
async def close_issue(platform: str, project_id: str, issue_id: str) -> Dict[str, Any]:
    """Close an issue"""
    return await PlatformService.close_issue(platform, project_id, issue_id)


# Merge Request Management Tools
@mcp.tool()
async def list_merge_requests(
    platform: str,
    project_id: str,
    state: str = "opened",
    limit: Optional[int] = 20,
    **filters,
) -> List[Dict[str, Any]]:
    """List merge requests in a project. State can be 'opened', 'closed', 'merged', or 'all'"""
    return await PlatformService.list_merge_requests(
        platform, project_id, state, limit, **filters
    )


@mcp.tool()
async def get_merge_request_details(
    platform: str, project_id: str, mr_id: str
) -> Dict[str, Any]:
    """Get detailed information about a specific merge request"""
    return await PlatformService.get_merge_request_details(platform, project_id, mr_id)


@mcp.tool()
async def create_merge_request(
    platform: str,
    project_id: str,
    title: str,
    source_branch: str,
    target_branch: str = "main",
    description: Optional[str] = None,
    assignee: Optional[str] = None,
    **kwargs,
) -> Dict[str, Any]:
    """Create a new merge request"""
    create_kwargs = kwargs.copy()
    if description:
        create_kwargs["description"] = description
    if assignee:
        create_kwargs["assignee_username"] = assignee

    return await PlatformService.create_merge_request(
        platform, project_id, title, source_branch, target_branch, **create_kwargs
    )


@mcp.tool()
async def list_my_merge_requests(
    platform: str,
    project_id: str,
    state: str = "opened",
    limit: Optional[int] = 20,
    **filters,
) -> List[Dict[str, Any]]:
    """List merge requests created by the current user (automatically uses configured username)"""
    return await PlatformService.list_my_merge_requests(
        platform, project_id, state, limit, **filters
    )


@mcp.resource("config://platforms")
async def get_platforms_config() -> Dict[str, Any]:
    """Get the current platforms configuration"""
    platforms = await PlatformService.list_platforms()

    from .core.config import get_config

    config = get_config()

    return {
        "platforms": {
            p["name"]: {"type": p["type"], "url": p["url"], "username": p["username"]}
            for p in platforms
        },
        "defaults": {
            "platform": config.defaults.platform,
            "output_format": config.defaults.output_format,
            "page_size": config.defaults.page_size,
            "timeout": config.defaults.timeout,
        },
    }


@mcp.resource("project://{platform}/{project_id}")
async def get_project_resource(platform: str, project_id: str) -> Dict[str, Any]:
    """Get project information as a resource"""
    return await PlatformService.get_project_details(platform, project_id)


def main():
    """Run the MCP server with stdio transport"""
    import sys

    # Handle --install-claude flag for easy Claude Code setup
    if len(sys.argv) > 1 and sys.argv[1] == "--install-claude":
        install_claude_integration()
        return

    mcp.run()


def install_claude_integration():
    """Install Claude Code integration and slash commands."""
    import subprocess
    import shutil
    from pathlib import Path

    print("🔧 Setting up Git MCP Server with Claude Code...")

    # Check if claude command is available
    if not shutil.which("claude"):
        print("❌ Claude Code CLI is not installed.")
        print("   Please install Claude Code first: https://claude.ai/code")
        return

    # Add MCP server to Claude Code
    print("📦 Adding MCP server to Claude Code (user scope)...")
    try:
        subprocess.run(
            ["claude", "mcp", "add", "-s", "user", "git-mcp-server", "git-mcp-server"],
            check=True,
        )
        print("✅ MCP server added successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to add MCP server: {e}")
        return

    # Install slash commands
    print("📋 Installing issue-to-code workflow slash commands...")

    # Get slash commands from package data
    try:
        import importlib.resources

        commands_dir = Path.home() / ".claude" / "commands"
        commands_dir.mkdir(parents=True, exist_ok=True)

        # Copy slash command files
        package = importlib.resources.files("git_mcp")
        claude_commands = package / "claude_commands"

        if claude_commands.is_dir():
            for command_file in claude_commands.iterdir():
                if command_file.suffix == ".md":
                    target_file = commands_dir / command_file.name
                    target_file.write_text(command_file.read_text())
                    print(f"   Installed: {command_file.name}")
        else:
            print("⚠️  Slash commands not found in package. Using embedded commands...")
            install_embedded_commands(commands_dir)

        print("✅ Slash commands installed successfully")

    except Exception as e:
        print(f"⚠️  Could not install from package resources: {e}")
        print("   Installing embedded commands...")
        install_embedded_commands(Path.home() / ".claude" / "commands")

    print("\n🎯 Setup completed! Next steps:")
    print("1. Configure a Git platform:")
    print("   git-mcp config add my-gitlab gitlab --url https://gitlab.com")
    print("\n2. Test the connection:")
    print("   git-mcp config test my-gitlab")
    print("\n3. Use the issue-to-code workflow in Claude Code:")
    print("   /issue <issue-url>")
    print("   /plan")
    print("   /implement")
    print("   /test")
    print("   /doc")
    print("   /pr <issue-id>")
    print("\n🎉 Happy issue-driven coding!")


def install_embedded_commands(commands_dir):
    """Install embedded slash commands as fallback."""
    commands_dir.mkdir(parents=True, exist_ok=True)

    # Embedded command definitions
    commands = {
        "issue.md": """---
description: Fetch and analyze GitLab/GitHub issue
argument-hint: [issue-url] or [platform] [project-id] [issue-id] (empty to list my issues)
---

# 🎯 Issue Analysis

**Arguments:** $ARGUMENTS

## Mode Selection

If no arguments provided, show **My Issues Dashboard**:
- List issues assigned to me across configured platforms
- Show priority, status, and project context
- Allow selection for detailed analysis

If arguments provided, analyze **Specific Issue**:
- Fetch issue details from URL or platform/project/issue-id
- Provide technical analysis and requirements
- Generate implementation suggestions

## Analysis Output

**For My Issues List:**
1. **Assigned Issues** - issues assigned to current user
2. **Recent Activity** - recently updated issues
3. **Priority Issues** - high priority or urgent items
4. **Selection Prompt** - choose issue for detailed analysis

**For Specific Issue:**
1. **Issue Overview** - title, description, labels, priority
2. **Technical Requirements** - what needs to be implemented
3. **Context Analysis** - review current codebase for related components
4. **Next Steps** - suggested approach for development

Use `/plan` after issue analysis to generate the development plan.
""",
        "plan.md": """---
description: Generate development plan based on issue analysis
argument-hint: [optional context or specific requirements]
allowed-tools: Bash(git *)
---

# 📋 Development Plan Generator

Generate a structured development plan based on the analyzed issue.

**Context:** $ARGUMENTS

## Plan Generation

Create a comprehensive development plan including:

1. **Branch Strategy** - suggest branch name and workflow
2. **File Structure** - what files need to be created/modified
3. **Implementation Steps** - ordered task breakdown
4. **Testing Strategy** - what tests are needed
5. **Documentation Updates** - README, docs, comments

## Repository Context

Analyze current repository structure:

!git branch -a
!git status
!find . -name "*.py" -o -name "*.js" -o -name "*.ts" | head -20

Based on the issue requirements and current codebase, provide a detailed implementation roadmap.

Use `/implement` to start coding based on this plan.
""",
        "implement.md": """---
description: Implement planned functionality with best practices
argument-hint: [optional specific component or step]
---

# 🔨 Implementation

Implement the planned functionality following best practices.

**Focus:** $ARGUMENTS

## Implementation Process

1. **Create Feature Branch** - based on development plan
2. **Code Implementation** - write high-quality, maintainable code
3. **Follow Conventions** - match existing code style and patterns
4. **Error Handling** - implement robust error handling
5. **Code Comments** - add necessary documentation

## Best Practices

- Follow existing project patterns and conventions
- Write clean, readable, and maintainable code
- Implement proper error handling and logging
- Add type hints and documentation
- Consider security implications

Use `/test` after implementation to generate comprehensive tests.
""",
        "test.md": """---
description: Generate comprehensive test suites
argument-hint: [optional test type or component focus]
---

# 🧪 Test Generation

Generate comprehensive test suites for implemented functionality.

**Focus:** $ARGUMENTS

## Test Strategy

1. **Unit Tests** - test individual functions and methods
2. **Integration Tests** - test component interactions
3. **Edge Cases** - test boundary conditions and error scenarios
4. **Mock External Dependencies** - isolate components for testing
5. **Test Coverage** - ensure comprehensive coverage

## Test Types

- **Happy Path Tests** - normal operation scenarios
- **Error Handling Tests** - exception and error conditions
- **Boundary Tests** - edge cases and limits
- **Integration Tests** - component interactions
- **Performance Tests** - if applicable

Use `/doc` after testing to update documentation.
""",
        "doc.md": """---
description: Update documentation and API docs
argument-hint: [optional doc type or component focus]
---

# 📚 Documentation Update

Update documentation to reflect implemented changes.

**Focus:** $ARGUMENTS

## Documentation Updates

1. **API Documentation** - update function/method documentation
2. **README Updates** - update usage examples and features
3. **Configuration Guide** - update setup and configuration docs
4. **Examples** - add practical usage examples
5. **Changelog** - document changes and improvements

## Documentation Types

- **Code Comments** - inline documentation for complex logic
- **Docstrings** - comprehensive function/class documentation
- **README** - user-facing documentation and examples
- **API Docs** - detailed API reference
- **Configuration** - setup and configuration guides

Use `/pr` after documentation to create the pull/merge request.
""",
        "pr.md": """---
description: Create pull/merge request and close related issue
argument-hint: [issue-id] [optional: target-branch]
allowed-tools: Bash(git *), mcp__git-mcp-server__*
---

# 🚀 Pull Request Creation

Create a pull/merge request and close the related issue.

**Issue ID:** $ARGUMENTS

## PR Creation Process

1. **Prepare Branch**
   !git add .
   !git status
   !git commit -m "Implement feature for issue #$ARGUMENTS"

2. **Push to Remote**
   !git push -u origin HEAD

3. **Create Pull/Merge Request**
   Using our MCP tools to create the PR/MR with:
   - Descriptive title linking to issue
   - Comprehensive description
   - Closes #$ARGUMENTS in description
   - Appropriate labels and reviewers

4. **PR Description Template**
   ```
   ## Summary
   Implements [feature description] as requested in issue #$ARGUMENTS

   ## Changes Made
   - [List of changes]

   ## Testing
   - [Test coverage details]

   ## Documentation
   - [Documentation updates]

   Closes #$ARGUMENTS
   ```

5. **Final Steps**
   - Link PR to original issue
   - Request code review
   - Monitor CI/CD pipeline
   - Address review feedback

**Workflow Complete!** From issue analysis to PR creation.
""",
        "README.md": """# Git MCP Issue-to-Code Workflow

These slash commands provide a complete issue-driven development workflow, integrated with our Git MCP server for automated development processes.

**Command Type:** User-level commands (available across all projects)
**Installation Location:** `~/.claude/commands/`

## 🚀 Complete Workflow

```bash
# 1. Analyze issue
/issue https://gitlab.com/group/project/-/issues/123

# 2. Generate development plan
/plan

# 3. Implement functionality
/implement

# 4. Write tests
/test

# 5. Update documentation
/doc

# 6. Create PR/MR
/pr 123
```

## 📋 Command Details

### `/issue` - Issue Analysis
- No arguments: Show my assigned issues list
- With arguments: Get specific issue details from GitLab/GitHub URL
- Analyze technical requirements and context
- Provide implementation suggestions

### `/plan` - Development Planning
- Generate development plan based on issue analysis
- Analyze current codebase structure
- Provide branch strategy and implementation steps

### `/implement` - Functionality Implementation
- Implement planned functionality
- Create feature branch
- Write high-quality code following project conventions

### `/test` - Test Generation
- Generate tests for implemented functionality
- Include unit tests, integration tests
- Handle edge cases and error scenarios

### `/doc` - Documentation Updates
- Update API documentation
- Add usage examples
- Update README and configuration guides

### `/pr` - Create PR/MR
- Commit code and push branch
- Create Pull Request or Merge Request
- Automatically link and close related issue

## 🛠️ Integration Features

### MCP Tools Integration
These commands leverage our Git MCP server tools:
- `get_issue_by_url()` - Parse URL and fetch issue
- `get_issue_details()` - Get detailed information
- `create_merge_request()` - Create MR
- `get_platform_config()` - Get configuration info

Start your automated issue-to-code development journey! 🚀
""",
    }

    # Write command files
    for filename, content in commands.items():
        command_file = commands_dir / filename
        command_file.write_text(content.strip())
        print(f"   Installed: {filename}")


if __name__ == "__main__":
    main()
