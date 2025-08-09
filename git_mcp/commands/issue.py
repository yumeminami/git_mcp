"""Issue management commands for git-mcp."""

import asyncio
import click

from ..core.exceptions import GitMCPError
from ..utils.platform import resolve_platform


def get_adapter(platform_config):
    """Get platform adapter based on configuration."""
    if platform_config.type == "gitlab":
        from ..platforms.gitlab import GitLabAdapter

        return GitLabAdapter(
            platform_config.url, platform_config.token, platform_config.username
        )
    elif platform_config.type == "github":
        from ..platforms.github import GitHubAdapter

        return GitHubAdapter(
            platform_config.url, platform_config.token, platform_config.username
        )
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
        platform_name, platform_config = resolve_platform(ctx, platform)

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
        platform_name, platform_config = resolve_platform(ctx, platform)

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
        platform_name, platform_config = resolve_platform(ctx, platform)

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
        platform_name, platform_config = resolve_platform(ctx, platform)

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
        platform_name, platform_config = resolve_platform(ctx, platform)

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


@click.command("my")
@click.option("--platform", help="Platform name")
@click.option(
    "--state",
    type=click.Choice(["opened", "closed", "all"]),
    default="opened",
    help="Issue state filter",
)
@click.option("--limit", type=int, default=20, help="Maximum number of results")
@click.pass_context
def list_my_issues(ctx, platform, state, limit):
    """List issues assigned to me across all projects."""

    async def _list_my_issues():
        formatter = ctx.obj.get_formatter()

        # Determine platform
        platform_name, platform_config = resolve_platform(ctx, platform)

        if not platform_config.username:
            raise ValueError(
                f"No username configured for platform '{platform_name}'. Please configure username first."
            )

        # Use the global search from PlatformService
        from ..services.platform_service import PlatformService

        filters = {"assignee": platform_config.username}
        issues = await PlatformService.list_all_issues(
            platform_name, state=state, limit=limit, **filters
        )

        if issues:
            from ..platforms.base import ResourceType

            # Convert issues dict to proper resource objects
            resource_objects = []
            for issue in issues:
                # Create a proper resource-like object
                obj = type(
                    "IssueResource",
                    (),
                    {
                        "id": issue["id"],
                        "title": issue["title"],
                        "description": issue.get("description", ""),
                        "url": issue.get("url", ""),
                        "author": issue.get("author"),
                        "assignee": issue.get("assignee"),
                        "state": type("State", (), {"value": issue["state"]})()
                        if issue.get("state")
                        else None,
                        "created_at": issue.get("created_at"),
                        "updated_at": issue.get("updated_at"),
                        "metadata": {
                            "labels": issue.get("labels", []),
                            "project_id": issue.get("project_id"),
                        },
                        "resource_type": ResourceType.ISSUE,
                        "platform": "gitlab",
                        "project_id": issue.get("project_id", ""),
                    },
                )()
                resource_objects.append(obj)

            formatter.format_resources(resource_objects)
            formatter.print_info(
                f"Found {len(issues)} issues assigned to {platform_config.username}"
            )
        else:
            formatter.print_info(
                f"No {state} issues assigned to {platform_config.username}"
            )

    try:
        asyncio.run(_list_my_issues())
    except GitMCPError as e:
        formatter = ctx.obj.get_formatter()
        formatter.print_error(str(e))
        ctx.exit(1)
    except Exception as e:
        formatter = ctx.obj.get_formatter()
        formatter.print_error(f"Error: {str(e)}")
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
        platform_name, platform_config = resolve_platform(ctx, platform)

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
            # Global search across all projects
            from ..services.platform_service import PlatformService

            # Parse query for special filters like assignee:username
            filters = {}
            search_query = query  # Make a copy to avoid variable scoping issues
            if "assignee:" in search_query:
                # Extract assignee from query like "assignee:username"
                parts = search_query.split()
                for part in parts:
                    if part.startswith("assignee:"):
                        assignee_value = part.split(":", 1)[1]
                        if (
                            assignee_value == "me"
                            or assignee_value == platform_config.username
                        ):
                            filters["assignee"] = platform_config.username
                        else:
                            filters["assignee"] = assignee_value
                        # Remove this part from search query
                        search_query = search_query.replace(part, "").strip()
                        break

            if search_query.strip():
                filters["search"] = search_query.strip()

            # Use the global search from PlatformService
            issues = await PlatformService.list_all_issues(
                platform_name, limit=limit or 20, **filters
            )

            if issues:
                from ..platforms.base import ResourceType

                # Convert issues dict to proper resource objects
                resource_objects = []
                for issue in issues:
                    # Create a proper resource-like object
                    obj = type(
                        "IssueResource",
                        (),
                        {
                            "id": issue["id"],
                            "title": issue["title"],
                            "description": issue.get("description", ""),
                            "url": issue.get("url", ""),
                            "author": issue.get("author"),
                            "assignee": issue.get("assignee"),
                            "state": type("State", (), {"value": issue["state"]})()
                            if issue.get("state")
                            else None,
                            "created_at": issue.get("created_at"),
                            "updated_at": issue.get("updated_at"),
                            "metadata": {
                                "labels": issue.get("labels", []),
                                "project_id": issue.get("project_id"),
                            },
                            "resource_type": ResourceType.ISSUE,
                            "platform": "gitlab",
                            "project_id": issue.get("project_id", ""),
                        },
                    )()
                    resource_objects.append(obj)

                formatter.format_resources(resource_objects)
            else:
                formatter.print_info(f"No issues found for query: '{search_query}'")

    try:
        asyncio.run(_search_issues())
    except GitMCPError as e:
        formatter = ctx.obj.get_formatter()
        formatter.print_error(str(e))
        ctx.exit(1)


# Commands to be added to the main CLI
issue_commands = [
    list_issues,
    list_my_issues,
    get_issue,
    create_issue,
    update_issue,
    close_issue,
    search_issues,
]
