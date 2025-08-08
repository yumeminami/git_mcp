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
async def list_my_issues(
    platform: str,
    project_id: str,
    state: str = "opened",
    limit: Optional[int] = 20,
    **filters,
) -> List[Dict[str, Any]]:
    """List issues assigned to the current user (automatically uses configured username)"""
    return await PlatformService.list_my_issues(
        platform, project_id, state, limit, **filters
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
    mcp.run()


if __name__ == "__main__":
    main()
