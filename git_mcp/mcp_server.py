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

    # Handle installation flags for easy setup
    if len(sys.argv) > 1:
        if sys.argv[1] == "--install-claude":
            install_claude_integration()
            return
        elif sys.argv[1] == "--install-gemini":
            install_gemini_integration()
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
                    if command_file.suffix == ".md":
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
                if command_file.suffix == ".toml":
                    target_file = commands_dir / command_file.name
                    target_file.write_text(command_file.read_text())
                    print(f"   Installed: {command_file.name}")
        else:
            raise FileNotFoundError("Gemini commands directory not found in package")
    except Exception as e:
        print(f"❌ Failed to install Gemini commands from package: {e}")
        print("   Please check that the package was installed correctly")
        return

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


if __name__ == "__main__":
    main()
