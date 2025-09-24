"""Git MCP Server - MCP interface for Git repository management."""

from typing import List, Dict, Any, Optional
import json
from mcp.server.fastmcp import FastMCP

from .services.platform_service import PlatformService
from .core.logging import setup_logging, get_logger


# Create the MCP server
mcp = FastMCP("Git MCP Server")

# Global logger for MCP server
logger = get_logger("git_mcp.mcp_server")


# Platform Management Tools
@mcp.tool()
async def list_platforms() -> List[Dict[str, str]]:
    """List all configured Git platforms (GitLab, GitHub, etc.)"""
    logger.debug("MCP Tool: list_platforms called")
    result = await PlatformService.list_platforms()
    logger.debug(f"MCP Tool: list_platforms returned {len(result)} platforms")
    return result


@mcp.tool()
async def test_platform_connection(platform: str) -> Dict[str, Any]:
    """Test connection to a configured platform"""
    logger.debug(f"MCP Tool: test_platform_connection called for platform '{platform}'")
    result = await PlatformService.test_platform_connection(platform)
    logger.debug(
        f"MCP Tool: test_platform_connection result: {result.get('success', False)}"
    )
    return result


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


@mcp.tool()
async def create_issue_comment(
    platform: str, project_id: str, issue_id: str, body: str, **kwargs
) -> Dict[str, Any]:
    """Create a comment on an issue"""
    return await PlatformService.create_issue_comment(
        platform, project_id, issue_id, body, **kwargs
    )


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
    target_project_id: Optional[str] = None,
    **kwargs,
) -> Dict[str, Any]:
    """Create a new merge request with cross-project support

    Args:
        platform: Git platform name (github, gitlab, etc.)
        project_id: Source project ID (for cross-project MRs) or project ID (for same-project MRs)
        title: Merge request title
        source_branch: Source branch name or 'owner:branch' format for cross-repo
        target_branch: Target branch name (default: 'main')
        description: Optional merge request description
        assignee: Optional assignee username
        target_project_id: Optional target project ID for cross-project merge requests
        **kwargs: Additional platform-specific parameters

    Returns:
        Dict containing merge request details

    Examples:
        # Same-project MR
        create_merge_request("gitlab", "123", "Fix bug", "feature-branch", "main")

        # Cross-project MR (fork to upstream)
        create_merge_request("gitlab", "456", "Fix bug", "feature-branch", "main",
                           target_project_id="123")

        # GitHub cross-repo PR (using branch format)
        create_merge_request("github", "upstream/repo", "Fix bug", "fork-owner:feature-branch", "main")
    """
    create_kwargs = kwargs.copy()

    # Some MCP clients pass a single 'kwargs' argument as a JSON string.
    # Parse and merge it so downstream adapters receive real keyword args.
    if "kwargs" in create_kwargs:
        nested_kwargs = create_kwargs.pop("kwargs")
        try:
            if isinstance(nested_kwargs, str):
                parsed = json.loads(nested_kwargs)
            else:
                parsed = nested_kwargs
            if isinstance(parsed, dict):
                for k, v in parsed.items():
                    # Do not overwrite explicitly provided keys
                    if k not in create_kwargs:
                        create_kwargs[k] = v
        except Exception as e:  # nosec B110 - best-effort parsing
            logger.warning(f"Failed to parse kwargs JSON: {e}")

    # Handle description from either parameter or kwargs
    final_description = description
    if not final_description and "description" in create_kwargs:
        final_description = create_kwargs.pop("description")

    # Normalize alternative field names that might be sent by some clients
    if not final_description and "body" in create_kwargs:
        # Some tools use 'body' (GitHub semantics). Normalize to 'description'.
        final_description = create_kwargs.pop("body")

    if final_description:
        create_kwargs["description"] = final_description
        logger.debug(
            f"MCP Server - description parameter set: {final_description[:100]}..."
            if len(final_description) > 100
            else f"MCP Server - description parameter set: {final_description}"
        )

    if assignee:
        create_kwargs["assignee_username"] = assignee

    if target_project_id:
        create_kwargs["target_project_id"] = target_project_id

    logger.debug(f"MCP Server - kwargs being passed: {list(create_kwargs.keys())}")
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


@mcp.tool()
async def get_merge_request_diff(
    platform: str, project_id: str, mr_id: str, **options
) -> Dict[str, Any]:
    """Get diff/changes for a merge request

    Args:
        platform: The platform name (e.g., 'gitlab', 'github')
        project_id: The project identifier
        mr_id: The merge request/pull request ID
        **options: Optional parameters:
            - format: Response format ('json', 'unified') - default: 'json'
            - include_diff: Include actual diff content (bool) - default: True

    Returns:
        Dict containing:
            - mr_id: The merge request ID
            - total_changes: Summary of additions, deletions, files changed
            - files: List of changed files with details
            - diff_format: Format of the response
            - truncated: Whether response was truncated
    """
    return await PlatformService.get_merge_request_diff(
        platform, project_id, mr_id, **options
    )


@mcp.tool()
async def get_merge_request_commits(
    platform: str, project_id: str, mr_id: str, **filters
) -> Dict[str, Any]:
    """Get commits for a merge request

    Args:
        platform: The platform name (e.g., 'gitlab', 'github')
        project_id: The project identifier
        mr_id: The merge request/pull request ID
        **filters: Optional filters for commit selection

    Returns:
        Dict containing:
            - mr_id: The merge request ID
            - total_commits: Number of commits
            - commits: List of commit details with sha, message, author, dates, etc.
    """
    return await PlatformService.get_merge_request_commits(
        platform, project_id, mr_id, **filters
    )


@mcp.tool()
async def close_merge_request(
    platform: str, project_id: str, mr_id: str, **kwargs
) -> Dict[str, Any]:
    """Close a merge request without merging

    Args:
        platform: The platform name (e.g., 'gitlab', 'github')
        project_id: The project identifier
        mr_id: The merge request/pull request ID
        **kwargs: Additional platform-specific parameters

    Returns:
        Dict containing:
            - merge_request: Updated merge request details
            - message: Success message
            - platform: The platform name
            - project_id: The project identifier
            - mr_id: The merge request ID
    """
    return await PlatformService.close_merge_request(
        platform, project_id, mr_id, **kwargs
    )


@mcp.tool()
async def update_merge_request(
    platform: str, project_id: str, mr_id: str, **kwargs
) -> Dict[str, Any]:
    """Update a merge request (title, description, etc.)

    Args:
        platform: The platform name (e.g., 'gitlab', 'github')
        project_id: The project identifier
        mr_id: The merge request/pull request ID
        **kwargs: Update parameters (title, description, state, etc.)

    Returns:
        Dict containing:
            - merge_request: Updated merge request details
            - message: Success message
            - platform: The platform name
            - project_id: The project identifier
            - mr_id: The merge request ID
    """
    return await PlatformService.update_merge_request(
        platform, project_id, mr_id, **kwargs
    )


# Fork operations
@mcp.tool()
async def create_fork(platform: str, project_id: str, **kwargs) -> Dict[str, Any]:
    """Create a fork of a repository

    Args:
        platform: The platform name (github, gitlab)
        project_id: The repository ID to fork (owner/repo for GitHub, numeric for GitLab)
        **kwargs: Platform-specific fork parameters
                 - GitHub: organization, name, default_branch_only
                 - GitLab: namespace, name, path
    """
    return await PlatformService.create_fork(platform, project_id, **kwargs)


@mcp.tool()
async def get_fork_info(platform: str, project_id: str) -> Dict[str, Any]:
    """Get fork information for a repository

    Args:
        platform: The platform name (github, gitlab)
        project_id: The repository ID to check

    Returns:
        Dictionary with fork status, parent repository, and other fork details
    """
    return await PlatformService.get_fork_info(platform, project_id)


@mcp.tool()
async def list_forks(
    platform: str, project_id: str, limit: Optional[int] = 20
) -> List[Dict[str, Any]]:
    """List forks of a repository

    Args:
        platform: The platform name (github, gitlab)
        project_id: The repository ID to list forks for
        limit: Maximum number of forks to return

    Returns:
        List of fork repositories
    """
    return await PlatformService.list_forks(platform, project_id, limit)


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
    from . import get_version

    # Handle command line arguments
    debug_mode = False
    if len(sys.argv) > 1:
        if "--debug" in sys.argv:
            debug_mode = True
            sys.argv.remove("--debug")  # Remove so other args processing works

        if sys.argv[1] == "--version":
            print(f"git-mcp-server {get_version()}")
            return
        elif sys.argv[1] == "--install-claude":
            install_claude_integration()
            return
        elif sys.argv[1] == "--install-gemini":
            install_gemini_integration()
            return
        elif sys.argv[1] == "--install-codex":
            install_codex_integration()
            return
        elif sys.argv[1] in ["--help", "-h"]:
            print("git-mcp-server - Git MCP Server")
            print(f"Version: {get_version()}")
            print()
            print("Usage: git-mcp-server [OPTIONS]")
            print()
            print("Options:")
            print("  --version          Show version and exit")
            print("  --debug            Enable debug logging")
            print("  --help, -h         Show this help message and exit")
            print("  --install-claude   Install Claude Code integration")
            print("  --install-gemini   Install Gemini CLI integration")
            print("  --install-codex    Install Codex integration")
            print()
            print("Environment Variables:")
            print(
                "  GIT_MCP_SERVER_LOG_LEVEL    Set log level (DEBUG, INFO, WARNING, ERROR)"
            )
            print("  GIT_MCP_SERVER_DEBUG        Enable debug mode (true/false)")
            print("  GIT_MCP_SERVER_LOG_FILE     Log to file path")
            print()
            print("Run without arguments to start the MCP server.")
            return

    # Setup logging based on debug flag or environment
    if debug_mode:
        setup_logging(debug=True)
        logger.info("MCP Server starting with debug logging enabled")
    else:
        # Still setup logging to respect environment variables
        setup_logging()

    mcp.run()


# Code Memory Content - Design Principles and Guidelines
# This content is automatically added to user configuration files during installation
CODE_MEMORY_CONTENT = """

## Simplicity-First Design Principles

### Core Design Principles (Hierarchical Priority)

#### 1. KISS Principle (Primary Priority)
- **Principle of Parsimony**: Select the most direct and comprehensible solution among available alternatives
- **Cognitive Load Minimization**: Prioritize code readability and maintainability over algorithmic sophistication
- **Single Problem Resolution**: Address one clearly defined problem per implementation unit
- **Standard Library Preference**: Utilize established libraries and conventional patterns rather than custom implementations
- **Explicit Solution Preference**: Default to obvious and transparent approaches when functionally equivalent

#### 2. YAGNI Principle (Secondary Priority)
- **Present Requirements Focus**: Implement only functionality required for current specifications
- **Feature Scope Constraint**: Exclude speculative parameters, options, or configuration mechanisms
- **Optimization Deferral**: Establish functional correctness before performance considerations
- **Speculative Feature Rejection**: Eliminate functionality implemented for hypothetical future requirements

#### 3. DRY Principle (Tertiary Priority)
- **Duplication Elimination**: Remove apparent code repetition while avoiding premature abstraction
- **Pattern-Based Extraction**: Extract common logic only after clear usage patterns emerge
- **Abstraction Threshold**: Prefer explicit duplication over speculative generalization

#### 4. SOLID Principles (Quaternary Priority, Minimal Application)
- **Single Responsibility**: Maintain one clearly defined purpose per functional unit
- **Principle Application Restraint**: Apply remaining SOLID principles without architectural over-engineering

### Anti-Patterns and Prohibited Practices

#### Over-Design Constraints
- **Architectural Complexity Prohibition**: Avoid elaborate system architectures for straightforward problems
- **Framework Development Restriction**: Implement scripts rather than generalized frameworks unless explicitly required
- **Abstraction Layer Limitation**: Minimize unnecessary abstraction layers
- **Generic Solution Avoidance**: Reject generic implementations for specific problem domains

#### Over-Analysis Restrictions
- **Edge Case Analysis Limitation**: Avoid comprehensive upfront edge case enumeration
- **Solution Adequacy Threshold**: Terminate design iteration at "sufficient" rather than "optimal" solutions
- **Hypothetical Scenario Exclusion**: Exclude optimization for speculative use cases
- **Decision Paralysis Prevention**: Establish clear decision points to prevent analysis stagnation

#### Defensive Programming Constraints
- **Input Validation Restriction**: Implement validation only for explicitly identified risk scenarios
- **Error Handling Minimization**: Apply error handling mechanisms only where failure modes are documented
- **Exception Wrapping Limitation**: Avoid comprehensive try-catch implementations without specific requirements
- **Caller Trust Principle**: Assume correct caller behavior until empirical evidence suggests otherwise
- **Failure Mode Simplification**: Implement rapid failure mechanisms rather than comprehensive error recovery

### Implementation Methodology

#### Required Practices
- Implement straightforward and immediately comprehensible code structures
- Utilize simple control flow mechanisms (conditional statements, iteration constructs)
- Prefer language built-in functions over custom implementations
- Design minimal, purpose-focused functions
- Employ semantically clear variable nomenclature
- Begin with the simplest functional solution
- Introduce complexity only when explicitly specified in requirements

#### Prohibited Practices
- Elaborate class hierarchy construction
- Universal configuration mechanism implementation
- Speculative defensive programming
- Premature scalability engineering
- Unnecessary indirection layer creation
- Abstract base class implementation without clear inheritance requirements
- Comprehensive logging and monitoring system implementation without specification

### Decision Framework Protocol

When evaluating implementation decisions, apply the following sequential evaluation criteria:

1. **Simplicity Assessment**: Does the solution minimize cognitive complexity and maximize comprehensibility?
2. **Requirement Necessity**: Is this functionality required for current specifications rather than hypothetical future needs?
3. **Duplication Analysis**: Does the implementation create obvious and problematic code repetition?
4. **Responsibility Clarity**: Does the implementation maintain a single, well-defined purpose?

**Default Resolution Protocol**: Select the simplest implementation that satisfies immediate problem requirements without additional complexity.

---
"""


def _validate_config_path(path, allowed_dirs=None):
    """
    Validate that a path is safe for configuration file operations.

    Args:
        path: Path to validate
        allowed_dirs: Optional list of allowed directory names (e.g., ['.codex', '.claude', '.gemini'])

    Returns:
        Path: Resolved and validated path

    Raises:
        ValueError: If path is unsafe or outside allowed directories
    """
    from pathlib import Path

    if allowed_dirs is None:
        allowed_dirs = [".codex", ".claude", ".gemini"]

    try:
        # Resolve the path and ensure it's absolute
        resolved_path = Path(path).expanduser().resolve()

        # Ensure it's under the user's home directory
        home_dir = Path.home().resolve()
        if not str(resolved_path).startswith(str(home_dir)):
            raise ValueError(f"Path {resolved_path} is not under user home directory")

        # Check if path is within allowed config directories
        relative_path = resolved_path.relative_to(home_dir)
        first_part = relative_path.parts[0] if relative_path.parts else ""

        if first_part not in allowed_dirs:
            raise ValueError(
                f"Path {resolved_path} is not in allowed directories: {allowed_dirs}"
            )

        return resolved_path

    except Exception as e:
        logger.error(f"Path validation failed for {path}: {e}")
        raise ValueError(f"Invalid or unsafe path: {path}") from e


def _append_code_memory_to_file(file_path):
    """
    Append code memory content to a file with idempotency check.

    Args:
        file_path (Path): Target file path

    Returns:
        bool: True if content was added, False if already exists or on error
    """
    from datetime import datetime

    try:
        # Validate path security before proceeding
        file_path = _validate_config_path(file_path)

        # Create parent directories if they don't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Check if content already exists (idempotency)
        if file_path.exists():
            existing_content = file_path.read_text()
            if "Simplicity-First Design Principles" in existing_content:
                logger.debug(f"Code memory content already exists in {file_path}")
                return False

        # Prepare content with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        content_to_add = CODE_MEMORY_CONTENT.format(timestamp=timestamp)

        # Append content to file
        with file_path.open("a", encoding="utf-8") as f:
            if file_path.exists() and file_path.stat().st_size > 0:
                f.write("\n")  # Add newline if file has content
            f.write(content_to_add)

        logger.debug(f"Code memory content appended to {file_path}")
        return True

    except ValueError as e:
        logger.warning(f"Invalid path for code memory file: {e}")
        print(f"❌ Invalid path: {e}")
        return False
    except PermissionError:
        logger.warning(f"Permission denied writing to {file_path}")
        print(f"⚠️  Could not write to {file_path} (permission denied)")
        return False
    except OSError as e:
        logger.warning(f"Error writing to {file_path}: {e}")
        print(f"⚠️  Could not write to {file_path}: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error writing to {file_path}: {e}")
        print(f"❌ Unexpected error writing to {file_path}: {e}")
        return False


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
        # First try to remove if exists, then add
        subprocess.run(
            ["claude", "mcp", "remove", "git-mcp-server"],
            capture_output=True,  # Don't show error if doesn't exist
        )
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
        try:
            claude_commands_ref = importlib.resources.files("git_mcp.claude_commands")
            if claude_commands_ref.is_dir():
                for command_file in claude_commands_ref.iterdir():
                    if command_file.name.endswith(".md"):
                        target_file = commands_dir / command_file.name
                        target_file.write_text(command_file.read_text())
                        print(f"   Installed: {command_file.name}")
                print("✅ Slash commands installed successfully")
            else:
                raise FileNotFoundError(
                    "Claude commands directory not found in package"
                )
        except Exception as e:
            print(f"❌ Failed to install Claude commands from package: {e}")
            print("   Please check that the package was installed correctly")
            return

    except Exception as e:
        print(f"❌ Failed to setup Claude commands: {e}")
        return

    # Add code memory guidelines to Claude configuration
    print("📝 Adding code memory guidelines to Claude configuration...")
    claude_config_file = Path.home() / ".claude" / "CLAUDE.md"
    if _append_code_memory_to_file(claude_config_file):
        print(f"✅ Code memory guidelines added to {claude_config_file}")
    else:
        print(f"ℹ️  Code memory guidelines already present in {claude_config_file}")

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


def install_gemini_integration():
    """Install Gemini CLI integration and slash commands."""
    import json
    import shutil
    from pathlib import Path

    print("🔧 Setting up Git MCP Server with Gemini CLI...")

    # Check if gemini command is available
    if not shutil.which("gemini"):
        print("❌ Gemini CLI is not installed.")
        print(
            "   Please install Gemini CLI first: https://github.com/google-gemini/gemini-cli"
        )
        return

    # Get Gemini settings path
    gemini_settings_path = Path.home() / ".gemini" / "settings.json"

    print("📦 Adding MCP server to Gemini CLI...")

    # Load or create settings
    settings = {}
    if gemini_settings_path.exists():
        try:
            settings = json.loads(gemini_settings_path.read_text())
        except Exception as e:
            print(f"⚠️  Could not parse existing settings: {e}")

    # Ensure mcpServers exists
    if "mcpServers" not in settings:
        settings["mcpServers"] = {}

    # Add our MCP server configuration
    settings["mcpServers"]["git-mcp-server"] = {
        "command": "git-mcp-server",
        "args": [],
        "env": {},
        "timeout": 30000,
        "trust": True,  # Trust our tools to avoid confirmation prompts
    }

    # Create settings directory if it doesn't exist
    gemini_settings_path.parent.mkdir(parents=True, exist_ok=True)

    # Write updated settings
    try:
        gemini_settings_path.write_text(json.dumps(settings, indent=2))
        print("✅ MCP server added successfully to Gemini settings")
    except Exception as e:
        print(f"❌ Failed to update Gemini settings: {e}")
        return

    # Install slash commands for Gemini
    print("📋 Installing issue-to-code workflow slash commands for Gemini...")

    commands_dir = Path.home() / ".gemini" / "commands"
    commands_dir.mkdir(parents=True, exist_ok=True)

    # Get Gemini commands from package data
    try:
        import importlib.resources

        gemini_commands_ref = importlib.resources.files("git_mcp.gemini_commands")
        if gemini_commands_ref.is_dir():
            for command_file in gemini_commands_ref.iterdir():
                if command_file.name.endswith(".toml"):
                    target_file = commands_dir / command_file.name
                    target_file.write_text(command_file.read_text())
                    print(f"   Installed: {command_file.name}")
        else:
            raise FileNotFoundError("Gemini commands directory not found in package")
    except Exception as e:
        print(f"❌ Failed to install Gemini commands from package: {e}")
        print("   Please check that the package was installed correctly")
        return

    # Add code memory guidelines to Gemini configuration
    print("📝 Adding code memory guidelines to Gemini configuration...")
    gemini_config_file = Path.home() / ".gemini" / "GEMINI.md"
    if _append_code_memory_to_file(gemini_config_file):
        print(f"✅ Code memory guidelines added to {gemini_config_file}")
    else:
        print(f"ℹ️  Code memory guidelines already present in {gemini_config_file}")

    print("\n🎯 Setup completed! Next steps:")
    print("1. Configure a Git platform:")
    print("   git-mcp config add my-gitlab gitlab --url https://gitlab.com")
    print("\n2. Test the connection:")
    print("   git-mcp config test my-gitlab")
    print("\n3. Use the issue-to-code workflow in Gemini CLI:")
    print("   /issue <issue-url>")
    print("   /plan")
    print("   /implement")
    print("   /test")
    print("   /doc")
    print("   /pr <issue-id>")
    print("\n🎉 Happy issue-driven coding with Gemini!")


def install_codex_integration() -> None:
    """
    Install Codex integration and slash commands.

    This function sets up the complete Codex integration by:
    1. Verifying Codex CLI is available
    2. Configuring MCP server in ~/.codex/config.toml
    3. Installing slash commands to ~/.codex/prompts/
    4. Adding code memory guidelines to ~/.codex/AGENTS.md

    The integration follows the same pattern as Claude Code and Gemini CLI
    integrations but adapts to Codex's specific configuration requirements.
    """
    import shutil

    print("🔧 Setting up Git MCP Server with Codex...")

    # Check if codex command is available and warn if not found
    if not shutil.which("codex"):
        print("⚠️  Codex CLI not found on PATH.")
        print(
            "   Installation will proceed, but you'll need to install Codex to use the integration."
        )
        print("   Get Codex at: https://github.com/openai/codex")
        print()

    # Configure MCP server in ~/.codex/config.toml
    print("📦 Adding MCP server to Codex configuration...")
    if not _configure_codex_mcp_server():
        return

    # Install slash commands to ~/.codex/prompts/
    print("📋 Installing issue-to-code workflow slash commands...")
    if not _install_codex_commands():
        return

    # Update AGENTS.md with code memory guidelines
    print("📝 Adding code memory guidelines to Codex configuration...")
    _update_codex_agents_memory()

    print("\n🎯 Setup completed! Next steps:")
    print("1. Configure a Git platform:")
    print("   git-mcp config add my-gitlab gitlab --url https://gitlab.com")
    print("\n2. Test the connection:")
    print("   git-mcp config test my-gitlab")
    print("\n3. Use the issue-to-code workflow in Codex:")
    print("   /issue <issue-url>")
    print("   /plan")
    print("   /implement")
    print("   /test")
    print("   /doc")
    print("   /pr <issue-id>")
    print("\n🎉 Happy issue-driven coding with Codex!")


def _configure_codex_mcp_server() -> bool:
    """
    Add MCP server configuration to Codex's config.toml file.

    Codex uses a TOML configuration file at ~/.codex/config.toml to define
    MCP servers. This function:
    1. Loads existing configuration (if any)
    2. Adds git-mcp-server to the [mcp_servers] section
    3. Writes the updated configuration back to the file

    Returns:
        bool: True if configuration was successful, False otherwise

    The configuration format follows Codex's MCP specification:
    [mcp_servers.git-mcp-server]
    command = "git-mcp-server"
    args = []
    env = {}
    """
    from pathlib import Path

    try:
        # Import TOML handling libraries with graceful fallbacks
        try:
            # Try Python 3.11+ built-in tomllib first
            from importlib import import_module

            tomllib = import_module("tomllib")
        except ImportError:
            try:
                # Fallback to tomli for older Python versions
                tomllib = import_module("tomli")
            except ImportError:
                print(
                    "❌ TOML support not available. Please install tomli: pip install tomli"
                )
                return False

        try:
            import tomli_w
        except ImportError:
            print(
                "❌ TOML writing support not available. Please install tomli-w: pip install tomli-w"
            )
            return False

        # Use secure path validation for config file
        config_file = _validate_config_path(Path.home() / ".codex" / "config.toml")

        # Create .codex directory if it doesn't exist
        config_file.parent.mkdir(parents=True, exist_ok=True)

        # Load existing config or create new
        config = {}
        if config_file.exists():
            try:
                config_content = config_file.read_text(encoding="utf-8")
                config = tomllib.loads(config_content)
                logger.debug(f"Loaded existing Codex config from {config_file}")
            except FileNotFoundError:
                logger.debug(f"Config file {config_file} not found, creating new")
            except PermissionError:
                print(f"❌ Permission denied reading {config_file}")
                return False
            except tomllib.TOMLDecodeError as e:
                print(f"❌ Invalid TOML syntax in {config_file}: {e}")
                print("   Please fix the syntax or delete the file to recreate it.")
                return False
            except UnicodeDecodeError as e:
                print(f"❌ Invalid encoding in {config_file}: {e}")
                return False
            except Exception as e:
                logger.warning(f"Unexpected error reading {config_file}: {e}")
                print(f"⚠️  Could not parse existing config.toml: {e}")
                print("   Continuing with empty configuration...")

        # Ensure mcp_servers section exists
        if "mcp_servers" not in config:
            config["mcp_servers"] = {}

        # Add our MCP server configuration
        config["mcp_servers"]["git-mcp-server"] = {
            "command": "git-mcp-server",
            "args": [],
            "env": {},
        }

        # Write updated config with proper error handling
        try:
            config_content = tomli_w.dumps(config)
            config_file.write_text(config_content, encoding="utf-8")
            logger.debug(f"Updated Codex config at {config_file}")
        except PermissionError:
            print(f"❌ Permission denied writing to {config_file}")
            return False
        except OSError as e:
            print(f"❌ Could not write to {config_file}: {e}")
            return False
        print("✅ MCP server added successfully to Codex configuration")
        return True

    except ValueError as e:
        print(f"❌ Invalid path for Codex configuration: {e}")
        return False
    except Exception as e:
        print(f"❌ Failed to configure Codex MCP server: {e}")
        return False


def _install_codex_commands() -> bool:
    """
    Install slash commands to ~/.codex/prompts/ directory.

    Codex looks for custom prompts in the ~/.codex/prompts/ directory.
    Each markdown file becomes a slash command (e.g., issue.md -> /issue).

    This function:
    1. Creates the prompts directory if it doesn't exist
    2. Copies all .md files from git_mcp.codex_commands package
    3. Reports the number of commands installed

    Returns:
        bool: True if installation was successful, False otherwise

    The command files include:
    - issue.md: Issue analysis and documentation
    - plan.md: Development planning
    - implement.md: Implementation execution
    - test.md: Testing automation
    - doc.md: Documentation updates
    - pr.md: Pull request creation
    """
    from pathlib import Path

    try:
        import importlib.resources

        # Create Codex prompts directory with secure path validation
        commands_dir = _validate_config_path(Path.home() / ".codex" / "prompts")
        commands_dir.mkdir(parents=True, exist_ok=True)

        # Copy slash command files from package
        try:
            codex_commands_ref = importlib.resources.files("git_mcp.codex_commands")
            if codex_commands_ref.is_dir():
                command_count = 0
                for command_file in codex_commands_ref.iterdir():
                    if command_file.name.endswith(".md"):
                        target_file = commands_dir / command_file.name
                        target_file.write_text(command_file.read_text())
                        print(f"   Installed: {command_file.name}")
                        command_count += 1

                if command_count > 0:
                    print(f"✅ {command_count} slash commands installed successfully")
                    return True
                else:
                    print("⚠️  No command files found in package")
                    return False
            else:
                raise FileNotFoundError("Codex commands directory not found in package")

        except Exception as e:
            print(f"❌ Failed to install Codex commands from package: {e}")
            print("   Please check that the package was installed correctly")
            return False

    except ValueError as e:
        print(f"❌ Invalid path for Codex commands: {e}")
        return False
    except Exception as e:
        print(f"❌ Failed to setup Codex commands: {e}")
        return False


def _update_codex_agents_memory() -> bool:
    """
    Update ~/.codex/AGENTS.md with code memory guidelines.

    Codex uses a hierarchical memory system with AGENTS.md files:
    1. ~/.codex/AGENTS.md - Global personal guidance
    2. Project root AGENTS.md - Shared project notes
    3. Current directory AGENTS.md - Feature-specific notes

    This function adds code memory guidelines from issue #38 to the global
    AGENTS.md file, providing Codex with context about coding standards,
    KISS principles, and simplicity-first design patterns.

    The guidelines help Codex understand project conventions and generate
    code that follows established patterns and best practices.
    """
    from pathlib import Path

    codex_agents_file = Path.home() / ".codex" / "AGENTS.md"
    if _append_code_memory_to_file(codex_agents_file):
        print(f"✅ Code memory guidelines added to {codex_agents_file}")
        return True
    else:
        print(f"ℹ️  Code memory guidelines already present in {codex_agents_file}")
        return False


if __name__ == "__main__":
    main()
