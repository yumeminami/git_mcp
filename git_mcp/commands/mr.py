"""Merge Request (MR) management commands for git-mcp."""

import asyncio
import click

from ..core.exceptions import GitMCPError


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


def get_current_branch():
    """Get current git branch if available."""
    try:
        import subprocess  # nosec B404 - Safe git command usage

        result = subprocess.run(  # nosec B603, B607 - Safe git command with fixed args
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


@click.command("list")
@click.option("--platform", help="Platform name")
@click.option("--project", help="Project ID (for project-specific MRs)")
@click.option("--group", help="Group ID (for group-level MRs)")
@click.option("--all", "all_mrs", is_flag=True, help="List all accessible MRs")
@click.option(
    "--state",
    type=click.Choice(["opened", "closed", "merged", "all"]),
    default="opened",
    help="MR state filter",
)
@click.option("--assignee", help="Filter by assignee username")
@click.option("--author", help="Filter by author username")
@click.option("--labels", help="Filter by labels (comma-separated)")
@click.option("--milestone", help="Filter by milestone")
@click.option("--search", help="Search in title and description")
@click.option("--source-branch", help="Filter by source branch")
@click.option("--target-branch", help="Filter by target branch")
@click.option("--limit", type=int, default=20, help="Maximum number of results")
@click.option(
    "--sort",
    type=click.Choice(["created_asc", "created_desc", "updated_asc", "updated_desc"]),
    default="updated_desc",
    help="Sort order",
)
@click.pass_context
def list_mrs(
    ctx,
    platform,
    project,
    group,
    all_mrs,
    state,
    assignee,
    author,
    labels,
    milestone,
    search,
    source_branch,
    target_branch,
    limit,
    sort,
):
    """List merge requests."""

    async def _list_mrs():
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

        # Validate scope options
        scope_count = sum([bool(project), bool(group), bool(all_mrs)])
        if scope_count == 0:
            raise ValueError(
                "Please specify --project, --group, or --all to define scope"
            )
        if scope_count > 1:
            raise ValueError("Please specify only one of --project, --group, or --all")

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
        if source_branch:
            filters["source_branch"] = source_branch
        if target_branch:
            filters["target_branch"] = target_branch

        # Handle sort parameter
        if sort:
            sort_mapping = {
                "created_asc": {"order_by": "created_at", "sort": "asc"},
                "created_desc": {"order_by": "created_at", "sort": "desc"},
                "updated_asc": {"order_by": "updated_at", "sort": "asc"},
                "updated_desc": {"order_by": "updated_at", "sort": "desc"},
            }
            if sort in sort_mapping:
                filters.update(sort_mapping[sort])

        adapter = get_adapter(platform_config)

        if project:
            # Project-specific MRs
            mrs = await adapter.list_merge_requests(project, **filters)
        elif group:
            # Group-level MRs (would need group adapter method)
            formatter.print_warning("Group-level MR listing not yet implemented")
            formatter.print_info("Please use --project for now")
            return
        else:
            # Global MRs (would need global adapter method)
            formatter.print_warning("Global MR listing not yet implemented")
            formatter.print_info("Please use --project for now")
            return

        # Apply limit
        if limit and len(mrs) > limit:
            mrs = mrs[:limit]

        if mrs:
            formatter.format_resources(mrs)
        else:
            formatter.print_info("No merge requests found matching the criteria")

    try:
        asyncio.run(_list_mrs())
    except GitMCPError as e:
        formatter = ctx.obj.get_formatter()
        formatter.print_error(str(e))
        ctx.exit(1)


@click.command("get")
@click.argument("project_id")
@click.argument("mr_id")
@click.option("--platform", help="Platform name")
@click.pass_context
def get_mr(ctx, project_id, mr_id, platform):
    """Get detailed information about a merge request."""

    async def _get_mr():
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
        mr = await adapter.get_merge_request(project_id, mr_id)

        if mr:
            formatter.format_single_resource(mr)
        else:
            formatter.print_error(
                f"Merge request '{mr_id}' not found in project '{project_id}'"
            )

    try:
        asyncio.run(_get_mr())
    except GitMCPError as e:
        formatter = ctx.obj.get_formatter()
        formatter.print_error(str(e))
        ctx.exit(1)


@click.command("create")
@click.argument("project_id")
@click.option("--platform", help="Platform name")
@click.option(
    "--source",
    "source_branch",
    default=None,
    help="Source branch (defaults to current branch)",
)
@click.option("--target", "target_branch", default="main", help="Target branch")
@click.option("--title", required=True, help="MR title")
@click.option("--description", help="MR description")
@click.option("--assignee", help="Assignee username")
@click.option("--reviewer", help="Reviewer username (GitLab 13.9+)")
@click.option("--labels", help="Labels (comma-separated)")
@click.option("--milestone", help="Milestone title")
@click.option("--draft", is_flag=True, help="Create as draft MR")
@click.option(
    "--remove-source-branch", is_flag=True, help="Remove source branch when merged"
)
@click.option("--squash", is_flag=True, help="Squash commits when merging")
@click.option("--allow-collaboration", is_flag=True, help="Allow collaboration on MR")
@click.pass_context
def create_mr(
    ctx,
    project_id,
    platform,
    source_branch,
    target_branch,
    title,
    description,
    assignee,
    reviewer,
    labels,
    milestone,
    draft,
    remove_source_branch,
    squash,
    allow_collaboration,
):
    """Create a new merge request."""

    async def _create_mr():
        nonlocal source_branch  # Allow modification of outer scope variable
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

        # Auto-detect source branch if not provided
        if source_branch is None or not source_branch:
            detected_branch = get_current_branch()
            if not detected_branch:
                raise ValueError(
                    "Could not detect current branch. Please specify --source"
                )
            source_branch = detected_branch
            formatter.print_info(f"Using current branch '{source_branch}' as source")

        # Build MR data
        mr_data = {}
        if description:
            mr_data["description"] = description
        if assignee:
            mr_data["assignee_id"] = assignee  # Will be resolved by adapter
        if reviewer:
            mr_data["reviewer_ids"] = [reviewer]  # Will be resolved by adapter
        if labels:
            mr_data["labels"] = [label.strip() for label in labels.split(",")]
        if milestone:
            mr_data["milestone"] = milestone
        if draft:
            mr_data["draft"] = True
        if remove_source_branch:
            mr_data["remove_source_branch"] = True
        if squash:
            mr_data["squash"] = True
        if allow_collaboration:
            mr_data["allow_collaboration"] = True

        adapter = get_adapter(platform_config)
        mr = await adapter.create_merge_request(
            project_id, source_branch, target_branch, title, **mr_data
        )

        formatter.print_success(f"Merge request '{title}' created successfully")
        formatter.format_single_resource(mr)

    try:
        asyncio.run(_create_mr())
    except GitMCPError as e:
        formatter = ctx.obj.get_formatter()
        formatter.print_error(str(e))
        ctx.exit(1)


@click.command("update")
@click.argument("project_id")
@click.argument("mr_id")
@click.option("--platform", help="Platform name")
@click.option("--title", help="New title")
@click.option("--description", help="New description")
@click.option("--assignee", help="New assignee username (use 'none' to unassign)")
@click.option("--labels", help="New labels (comma-separated)")
@click.option("--milestone", help="New milestone title (use 'none' to remove)")
@click.option("--target-branch", help="New target branch")
@click.option(
    "--state", type=click.Choice(["opened", "closed"]), help="Change MR state"
)
@click.option("--draft", type=bool, help="Set draft status (true/false)")
@click.pass_context
def update_mr(
    ctx,
    project_id,
    mr_id,
    platform,
    title,
    description,
    assignee,
    labels,
    milestone,
    target_branch,
    state,
    draft,
):
    """Update an existing merge request."""

    async def _update_mr():
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
        if target_branch:
            update_data["target_branch"] = target_branch
        if state:
            if state == "closed":
                update_data["state_event"] = "close"
            else:
                update_data["state_event"] = "reopen"
        if draft is not None:
            update_data["draft"] = draft

        if not update_data:
            formatter.print_warning("No updates specified")
            return

        # For MR updates, we need to use the update method if it exists,
        # or fall back to individual update calls
        adapter = get_adapter(platform_config)

        # Since our adapter might not have update_merge_request,
        # we'll get the current MR and update it
        try:
            # Get current MR
            mr = await adapter.get_merge_request(project_id, mr_id)
            if not mr:
                formatter.print_error(f"Merge request '{mr_id}' not found")
                return

            # This would require implementing update_merge_request in the adapter
            # For now, show what would be updated
            formatter.print_success(f"Merge request '{mr_id}' would be updated with:")
            for key, value in update_data.items():
                formatter.print_info(f"  {key}: {value}")
            formatter.print_warning(
                "MR update functionality needs to be implemented in the adapter"
            )

        except Exception as e:
            formatter.print_error(f"Failed to update merge request: {e}")

    try:
        asyncio.run(_update_mr())
    except GitMCPError as e:
        formatter = ctx.obj.get_formatter()
        formatter.print_error(str(e))
        ctx.exit(1)


@click.command("approve")
@click.argument("project_id")
@click.argument("mr_id")
@click.option("--platform", help="Platform name")
@click.option("--comment", help="Optional approval comment")
@click.option("--sha", help="Specific commit SHA to approve")
@click.pass_context
def approve_mr(ctx, project_id, mr_id, platform, comment, sha):
    """Approve a merge request."""

    async def _approve_mr():
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

        # Build approval data
        approval_data = {}
        if comment:
            approval_data["comment"] = comment
        if sha:
            approval_data["sha"] = sha

        adapter = get_adapter(platform_config)
        success = await adapter.approve_merge_request(
            project_id, mr_id, **approval_data
        )

        if success:
            formatter.print_success(f"Merge request '{mr_id}' approved successfully")
        else:
            formatter.print_error(f"Failed to approve merge request '{mr_id}'")

    try:
        asyncio.run(_approve_mr())
    except GitMCPError as e:
        formatter = ctx.obj.get_formatter()
        formatter.print_error(str(e))
        ctx.exit(1)


@click.command("merge")
@click.argument("project_id")
@click.argument("mr_id")
@click.option("--platform", help="Platform name")
@click.option("--merge-commit-message", help="Custom merge commit message")
@click.option("--squash-commit-message", help="Custom squash commit message")
@click.option(
    "--should-remove-source-branch",
    is_flag=True,
    help="Remove source branch after merge",
)
@click.option(
    "--merge-when-pipeline-succeeds", is_flag=True, help="Merge when pipeline succeeds"
)
@click.option("--squash", is_flag=True, help="Squash commits when merging")
@click.pass_context
def merge_mr(
    ctx,
    project_id,
    mr_id,
    platform,
    merge_commit_message,
    squash_commit_message,
    should_remove_source_branch,
    merge_when_pipeline_succeeds,
    squash,
):
    """Merge a merge request."""

    async def _merge_mr():
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

        # Build merge data
        merge_data = {}
        if merge_commit_message:
            merge_data["merge_commit_message"] = merge_commit_message
        if squash_commit_message:
            merge_data["squash_commit_message"] = squash_commit_message
        if should_remove_source_branch:
            merge_data["should_remove_source_branch"] = True
        if merge_when_pipeline_succeeds:
            merge_data["merge_when_pipeline_succeeds"] = True
        if squash:
            merge_data["squash"] = True

        adapter = get_adapter(platform_config)
        mr = await adapter.merge_merge_request(project_id, mr_id, **merge_data)

        formatter.print_success(f"Merge request '{mr_id}' merged successfully")
        formatter.format_single_resource(mr)

    try:
        asyncio.run(_merge_mr())
    except GitMCPError as e:
        formatter = ctx.obj.get_formatter()
        formatter.print_error(str(e))
        ctx.exit(1)


@click.command("close")
@click.argument("project_id")
@click.argument("mr_id")
@click.option("--platform", help="Platform name")
@click.option("--comment", help="Optional closing comment")
@click.pass_context
def close_mr(ctx, project_id, mr_id, platform, comment):
    """Close a merge request."""

    async def _close_mr():
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

        # Close MR by updating its state
        # We need to implement a close method or use update with state_event
        # For now, show what would happen
        formatter.print_success(f"Merge request '{mr_id}' would be closed")
        if comment:
            formatter.print_info(f"With comment: {comment}")
        formatter.print_warning(
            "MR close functionality needs to be implemented in the adapter"
        )

    try:
        asyncio.run(_close_mr())
    except GitMCPError as e:
        formatter = ctx.obj.get_formatter()
        formatter.print_error(str(e))
        ctx.exit(1)


# Commands to be added to the main CLI
mr_commands = [
    list_mrs,
    get_mr,
    create_mr,
    update_mr,
    approve_mr,
    merge_mr,
    close_mr,
]
