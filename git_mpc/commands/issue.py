"""Issue management commands for git-mcp."""

import asyncio
import click

from ..core.exceptions import GitMCPError


def get_adapter(platform_config):
    """Get platform adapter based on configuration."""
    if platform_config.type == "gitlab":
        from ..platforms.gitlab import GitLabAdapter

        return GitLabAdapter(platform_config.url, platform_config.token)
    else:
        raise ValueError(f"Platform type '{platform_config.type}' not supported yet")


@click.command("list")
@click.argument("project_id")
@click.option("--platform", help="Platform name")
@click.option(
    "--state",
    type=click.Choice(["opened", "closed", "all"]),
    default="opened",
    help="Issue state filter",
)
@click.option("--assignee", help="Filter by assignee username")
@click.option("--author", help="Filter by author username")
@click.option("--labels", help="Filter by labels (comma-separated)")
@click.option("--milestone", help="Filter by milestone")
@click.option("--search", help="Search in title and description")
@click.option("--limit", type=int, default=20, help="Maximum number of results")
@click.option(
    "--sort",
    type=click.Choice(["created_asc", "created_desc", "updated_asc", "updated_desc"]),
    default="updated_desc",
    help="Sort order",
)
@click.pass_context
def list_issues(
    ctx,
    project_id,
    platform,
    state,
    assignee,
    author,
    labels,
    milestone,
    search,
    limit,
    sort,
):
    """List issues for a project."""

    async def _list_issues():
        formatter = ctx.obj.get_formatter()

        # Determine which platform to use
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

        # Build filters
        filters = {}
        if state != "all":
            filters["state"] = state
        if assignee:
            filters["assignee"] = assignee
        if author:
            filters["author"] = author
        if labels:
            filters["labels"] = [label.strip() for label in labels.split(",")]
        if milestone:
            filters["milestone"] = milestone
        if search:
            filters["search"] = search

        # Handle sort parameter - GitLab specific mapping
        if sort:
            sort_mapping = {
                "created_asc": {"order_by": "created_at", "sort": "asc"},
                "created_desc": {"order_by": "created_at", "sort": "desc"},
                "updated_asc": {"order_by": "updated_at", "sort": "asc"},
                "updated_desc": {"order_by": "updated_at", "sort": "desc"},
            }
            if sort in sort_mapping:
                filters.update(sort_mapping[sort])

        # Get adapter and fetch issues
        adapter = get_adapter(platform_config)
        issues = await adapter.list_issues(project_id, **filters)

        # Apply limit
        if limit and len(issues) > limit:
            issues = issues[:limit]

        if issues:
            formatter.format_resources(issues)
        else:
            formatter.print_info("No issues found matching the criteria")

    try:
        asyncio.run(_list_issues())
    except GitMCPError as e:
        formatter = ctx.obj.get_formatter()
        formatter.print_error(str(e))
        ctx.exit(1)


@click.command("get")
@click.argument("project_id")
@click.argument("issue_id")
@click.option("--platform", help="Platform name")
@click.pass_context
def get_issue(ctx, project_id, issue_id, platform):
    """Get detailed information about an issue."""

    async def _get_issue():
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
        issue = await adapter.get_issue(project_id, issue_id)

        if issue:
            formatter.format_single_resource(issue)
        else:
            formatter.print_error(
                f"Issue '{issue_id}' not found in project '{project_id}'"
            )

    try:
        asyncio.run(_get_issue())
    except GitMCPError as e:
        formatter = ctx.obj.get_formatter()
        formatter.print_error(str(e))
        ctx.exit(1)


@click.command("create")
@click.argument("project_id")
@click.argument("title")
@click.option("--platform", help="Platform name")
@click.option("--description", help="Issue description")
@click.option("--assignee", help="Assignee username")
@click.option("--labels", help="Labels (comma-separated)")
@click.option("--milestone", help="Milestone title")
@click.option("--due-date", help="Due date (YYYY-MM-DD)")
@click.option(
    "--confidential", is_flag=True, help="Mark issue as confidential (GitLab only)"
)
@click.option(
    "--issue-type",
    type=click.Choice(["issue", "incident", "test_case"]),
    default="issue",
    help="Issue type (GitLab only)",
)
@click.pass_context
def create_issue(
    ctx,
    project_id,
    title,
    platform,
    description,
    assignee,
    labels,
    milestone,
    due_date,
    confidential,
    issue_type,
):
    """Create a new issue."""

    async def _create_issue():
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

        # Build issue data
        issue_data = {}
        if description:
            issue_data["description"] = description
        if assignee:
            issue_data["assignee_id"] = assignee  # Will be resolved by the adapter
        if labels:
            issue_data["labels"] = [label.strip() for label in labels.split(",")]
        if milestone:
            issue_data["milestone"] = milestone
        if due_date:
            issue_data["due_date"] = due_date
        if confidential:
            issue_data["confidential"] = True
        if issue_type != "issue":
            issue_data["issue_type"] = issue_type

        adapter = get_adapter(platform_config)
        issue = await adapter.create_issue(project_id, title, **issue_data)

        formatter.print_success(f"Issue '{title}' created successfully")
        formatter.format_single_resource(issue)

    try:
        asyncio.run(_create_issue())
    except GitMCPError as e:
        formatter = ctx.obj.get_formatter()
        formatter.print_error(str(e))
        ctx.exit(1)


@click.command("update")
@click.argument("project_id")
@click.argument("issue_id")
@click.option("--platform", help="Platform name")
@click.option("--title", help="New title")
@click.option("--description", help="New description")
@click.option("--assignee", help="New assignee username (use 'none' to unassign)")
@click.option("--labels", help="New labels (comma-separated)")
@click.option("--milestone", help="New milestone title (use 'none' to remove)")
@click.option("--due-date", help="New due date (YYYY-MM-DD, use 'none' to remove)")
@click.option(
    "--state", type=click.Choice(["opened", "closed"]), help="Change issue state"
)
@click.pass_context
def update_issue(
    ctx,
    project_id,
    issue_id,
    platform,
    title,
    description,
    assignee,
    labels,
    milestone,
    due_date,
    state,
):
    """Update an existing issue."""

    async def _update_issue():
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

        # Build update data
        update_data = {}
        if title:
            update_data["title"] = title
        if description:
            update_data["description"] = description
        if assignee:
            if assignee.lower() == "none":
                update_data["assignee_ids"] = []
            else:
                update_data["assignee_id"] = assignee
        if labels:
            update_data["labels"] = [label.strip() for label in labels.split(",")]
        if milestone:
            if milestone.lower() == "none":
                update_data["milestone"] = ""
            else:
                update_data["milestone"] = milestone
        if due_date:
            if due_date.lower() == "none":
                update_data["due_date"] = ""
            else:
                update_data["due_date"] = due_date
        if state:
            if state == "closed":
                update_data["state_event"] = "close"
            else:
                update_data["state_event"] = "reopen"

        if not update_data:
            formatter.print_warning("No updates specified")
            return

        adapter = get_adapter(platform_config)
        issue = await adapter.update_issue(project_id, issue_id, **update_data)

        formatter.print_success(f"Issue '{issue_id}' updated successfully")
        formatter.format_single_resource(issue)

    try:
        asyncio.run(_update_issue())
    except GitMCPError as e:
        formatter = ctx.obj.get_formatter()
        formatter.print_error(str(e))
        ctx.exit(1)


@click.command("close")
@click.argument("project_id")
@click.argument("issue_id")
@click.option("--platform", help="Platform name")
@click.option("--comment", help="Optional closing comment")
@click.pass_context
def close_issue(ctx, project_id, issue_id, platform, comment):
    """Close an issue."""

    async def _close_issue():
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

        # Build close data
        close_data = {}
        if comment:
            close_data["comment"] = comment

        adapter = get_adapter(platform_config)
        issue = await adapter.close_issue(project_id, issue_id, **close_data)

        formatter.print_success(f"Issue '{issue_id}' closed successfully")
        formatter.format_single_resource(issue)

    try:
        asyncio.run(_close_issue())
    except GitMCPError as e:
        formatter = ctx.obj.get_formatter()
        formatter.print_error(str(e))
        ctx.exit(1)


@click.command("search")
@click.option("--platform", help="Platform name")
@click.option("--query", required=True, help="Search query")
@click.option("--project", help="Project ID or namespace/name")
@click.option(
    "--scope",
    type=click.Choice(["issues", "merge_requests", "projects"]),
    default="issues",
    help="Search scope",
)
@click.option("--limit", type=int, default=20, help="Maximum number of results")
@click.pass_context
def search_issues(ctx, platform, query, project, scope, limit):
    """Search issues across projects."""

    async def _search_issues():
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

        if project and scope == "issues":
            # Search within a specific project
            filters = {"search": query}
            issues = await adapter.list_issues(project, **filters)

            # Apply limit
            if limit and len(issues) > limit:
                issues = issues[:limit]

            if issues:
                formatter.format_resources(issues)
            else:
                formatter.print_info(f"No issues found for query: '{query}'")
        else:
            formatter.print_warning(
                "Global search across all projects not yet implemented"
            )
            formatter.print_info("Please specify a --project for now")

    try:
        asyncio.run(_search_issues())
    except GitMCPError as e:
        formatter = ctx.obj.get_formatter()
        formatter.print_error(str(e))
        ctx.exit(1)


# Commands to be added to the main CLI
issue_commands = [
    list_issues,
    get_issue,
    create_issue,
    update_issue,
    close_issue,
    search_issues,
]
