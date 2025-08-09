"""Project management commands for git-mcp."""

import asyncio
import click

from ..core.exceptions import GitMCPError
from ..utils.platform import resolve_platform


def get_adapter(platform_config):
    """Get platform adapter based on configuration."""
    if platform_config.type == "gitlab":
        from ..platforms.gitlab import GitLabAdapter

        return GitLabAdapter(platform_config.url, platform_config.token)
    elif platform_config.type == "github":
        from ..platforms.github import GitHubAdapter

        return GitHubAdapter(platform_config.url, platform_config.token)
    else:
        raise ValueError(f"Platform type '{platform_config.type}' not supported yet")


@click.command("list")
@click.option("--platform", help="Platform name")
@click.option(
    "--visibility",
    type=click.Choice(["public", "internal", "private"]),
    help="Project visibility",
)
@click.option("--archived", type=bool, help="Include archived projects")
@click.option("--owned", type=bool, help="Only owned projects")
@click.option("--starred", type=bool, help="Only starred projects")
@click.option("--search", help="Search term")
@click.option("--limit", type=int, default=20, help="Maximum number of results")
@click.pass_context
def list_projects(ctx, platform, visibility, archived, owned, starred, search, limit):
    """List projects."""

    async def _list_projects():
        formatter = ctx.obj.get_formatter()

        # Determine which platform to use
        platform_name, platform_config = resolve_platform(ctx, platform)

        # Build filters
        filters = {}
        if visibility:
            filters["visibility"] = visibility
        if archived is not None:
            filters["archived"] = archived
        if owned is not None:
            filters["owned"] = owned
        if starred is not None:
            filters["starred"] = starred
        if search:
            filters["search"] = search

        # Get adapter and fetch projects
        adapter = get_adapter(platform_config)
        projects = await adapter.list_projects(**filters)

        # Apply limit
        if limit and len(projects) > limit:
            projects = projects[:limit]

        formatter.format_resources(projects)

    try:
        asyncio.run(_list_projects())
    except GitMCPError as e:
        formatter = ctx.obj.get_formatter()
        formatter.print_error(str(e))
        ctx.exit(1)


@click.command("get")
@click.argument("project_id")
@click.option("--platform", help="Platform name")
@click.pass_context
def get_project(ctx, project_id, platform):
    """Get detailed information about a project."""

    async def _get_project():
        formatter = ctx.obj.get_formatter()

        # Determine platform
        platform_name = platform or ctx.obj.platform
        if not platform_name:
            available_platforms = ctx.obj.config.list_platforms()
            if len(available_platforms) == 1:
                platform_name = available_platforms[0]
            else:
                raise ValueError("Please specify --platform or set a default platform")

        platform_config = ctx.obj.config.get_platform(platform_name)
        if not platform_config:
            raise ValueError(f"Platform '{platform_name}' not configured")

        adapter = get_adapter(platform_config)
        project = await adapter.get_project(project_id)

        if project:
            formatter.format_single_resource(project)
        else:
            formatter.print_error(f"Project '{project_id}' not found")

    try:
        asyncio.run(_get_project())
    except GitMCPError as e:
        formatter = ctx.obj.get_formatter()
        formatter.print_error(str(e))
        ctx.exit(1)


@click.command("create")
@click.argument("name")
@click.option("--platform", help="Platform name")
@click.option("--description", help="Project description")
@click.option(
    "--visibility",
    type=click.Choice(["public", "internal", "private"]),
    default="private",
    help="Project visibility",
)
@click.option("--initialize-with-readme", is_flag=True, help="Initialize with README")
@click.pass_context
def create_project(
    ctx, name, platform, description, visibility, initialize_with_readme
):
    """Create a new project."""

    async def _create_project():
        formatter = ctx.obj.get_formatter()

        # Determine platform
        platform_name = platform or ctx.obj.platform
        if not platform_name:
            available_platforms = ctx.obj.config.list_platforms()
            if len(available_platforms) == 1:
                platform_name = available_platforms[0]
            else:
                raise ValueError("Please specify --platform or set a default platform")

        platform_config = ctx.obj.config.get_platform(platform_name)
        if not platform_config:
            raise ValueError(f"Platform '{platform_name}' not configured")

        # Build project data
        project_data = {"visibility": visibility}
        if description:
            project_data["description"] = description
        if initialize_with_readme:
            project_data["initialize_with_readme"] = True

        adapter = get_adapter(platform_config)
        project = await adapter.create_project(name, **project_data)

        formatter.print_success(f"Project '{name}' created successfully")
        formatter.format_single_resource(project)

    try:
        asyncio.run(_create_project())
    except GitMCPError as e:
        formatter = ctx.obj.get_formatter()
        formatter.print_error(str(e))
        ctx.exit(1)


@click.command("delete")
@click.argument("project_id")
@click.option("--platform", help="Platform name")
@click.confirmation_option(prompt="Are you sure you want to delete this project?")
@click.pass_context
def delete_project(ctx, project_id, platform):
    """Delete a project."""

    async def _delete_project():
        formatter = ctx.obj.get_formatter()

        # Determine platform
        platform_name = platform or ctx.obj.platform
        if not platform_name:
            available_platforms = ctx.obj.config.list_platforms()
            if len(available_platforms) == 1:
                platform_name = available_platforms[0]
            else:
                raise ValueError("Please specify --platform or set a default platform")

        platform_config = ctx.obj.config.get_platform(platform_name)
        if not platform_config:
            raise ValueError(f"Platform '{platform_name}' not configured")

        adapter = get_adapter(platform_config)
        success = await adapter.delete_project(project_id)

        if success:
            formatter.print_success(f"Project '{project_id}' deleted successfully")
        else:
            formatter.print_error(f"Failed to delete project '{project_id}'")

    try:
        asyncio.run(_delete_project())
    except GitMCPError as e:
        formatter = ctx.obj.get_formatter()
        formatter.print_error(str(e))
        ctx.exit(1)


# Commands to be added to the main CLI
project_commands = [list_projects, get_project, create_project, delete_project]
