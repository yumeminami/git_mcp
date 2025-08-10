"""GitLab platform adapter for git-mcp."""

import gitlab
from gitlab.exceptions import GitlabError, GitlabAuthenticationError
from typing import Dict, List, Optional, Any
from datetime import datetime

from .base import (
    PlatformAdapter,
    ProjectResource,
    IssueResource,
    MergeRequestResource,
    ResourceType,
    ResourceState,
)
from ..core.exceptions import (
    AuthenticationError,
    PlatformError,
    ResourceNotFoundError,
    NetworkError,
)


class GitLabAdapter(PlatformAdapter):
    """GitLab platform adapter using python-gitlab."""

    def __init__(
        self,
        url: str = "https://gitlab.com",
        token: Optional[str] = None,
        username: Optional[str] = None,
    ):
        super().__init__(url, token, username)
        self.client: Optional[gitlab.Gitlab] = None

    @property
    def platform_name(self) -> str:
        return "gitlab"

    async def authenticate(self) -> bool:
        """Authenticate with GitLab."""
        if not self.token:
            raise AuthenticationError("GitLab token is required")

        try:
            self.client = gitlab.Gitlab(self.url, private_token=self.token)
            self.client.auth()
            self._authenticated = True
            return True
        except GitlabAuthenticationError as e:
            raise AuthenticationError(f"GitLab authentication failed: {e}")
        except Exception as e:
            raise NetworkError(f"Failed to connect to GitLab: {e}")

    async def test_connection(self) -> bool:
        """Test connection to GitLab."""
        if not self.client:
            await self.authenticate()

        try:
            self.client.user
            return True
        except Exception:
            return False

    # Project operations
    async def list_projects(self, **filters) -> List[ProjectResource]:
        """List GitLab projects."""
        if not self.client:
            await self.authenticate()

        try:
            # Convert common filters to GitLab format
            gitlab_filters = self._normalize_project_filters(filters)
            projects = self.client.projects.list(all=True, **gitlab_filters)

            return [self._convert_to_project_resource(p) for p in projects]
        except GitlabError as e:
            raise PlatformError(f"Failed to list projects: {e}", self.platform_name)

    async def get_project(self, project_id: str) -> Optional[ProjectResource]:
        """Get a specific GitLab project."""
        if not self.client:
            await self.authenticate()

        try:
            project = self.client.projects.get(project_id)
            return self._convert_to_project_resource(project)
        except GitlabError as e:
            if e.response_code == 404:
                return None
            raise PlatformError(
                f"Failed to get project {project_id}: {e}", self.platform_name
            )

    async def create_project(self, name: str, **kwargs) -> ProjectResource:
        """Create a new GitLab project."""
        if not self.client:
            await self.authenticate()

        try:
            project_data = {"name": name, **kwargs}
            project = self.client.projects.create(project_data)
            return self._convert_to_project_resource(project)
        except GitlabError as e:
            raise PlatformError(f"Failed to create project: {e}", self.platform_name)

    async def delete_project(self, project_id: str) -> bool:
        """Delete a GitLab project."""
        if not self.client:
            await self.authenticate()

        try:
            project = self.client.projects.get(project_id)
            project.delete()
            return True
        except GitlabError as e:
            if e.response_code == 404:
                raise ResourceNotFoundError("project", project_id, self.platform_name)
            raise PlatformError(
                f"Failed to delete project {project_id}: {e}", self.platform_name
            )

    # Issue operations
    async def list_issues(self, project_id: str, **filters) -> List[IssueResource]:
        """List issues for a GitLab project."""
        if not self.client:
            await self.authenticate()

        try:
            project = self.client.projects.get(project_id)
            gitlab_filters = self._normalize_issue_filters(filters)
            issues = project.issues.list(all=True, **gitlab_filters)

            return [
                self._convert_to_issue_resource(issue, project_id) for issue in issues
            ]
        except GitlabError as e:
            raise PlatformError(f"Failed to list issues: {e}", self.platform_name)

    async def list_all_issues(self, **filters) -> List[IssueResource]:
        """List issues across all projects (global search)."""
        if not self.client:
            await self.authenticate()

        try:
            gitlab_filters = self._normalize_issue_filters(filters)

            # Handle assignee filter - use optimal approach
            assignee_filter = None
            if "assignee" in filters:
                assignee_filter = filters["assignee"]

                # Check if searching for current user - use scope=assigned_to_me for optimal performance
                if assignee_filter == self.username:
                    # Use the most efficient approach for current user
                    gitlab_filters = {
                        "scope": "assigned_to_me",
                        "state": gitlab_filters.get("state", "opened"),
                        "all": False,
                        "per_page": 100,
                    }
                    # Add other filters if present
                    if "labels" in gitlab_filters:
                        gitlab_filters["labels"] = gitlab_filters["labels"]
                else:
                    # For other users, try to get assignee ID
                    try:
                        users = self.client.users.list(username=assignee_filter)
                        if users:
                            gitlab_filters["assignee_id"] = users[0].id
                            # Remove the username-based filter
                            gitlab_filters.pop("assignee_username", None)
                        else:
                            # User not found, will return empty results
                            return []
                    except Exception:
                        # If we can't get the user ID, fall back to client-side filtering
                        assignee_filter = (
                            assignee_filter  # Keep for client-side filtering
                        )

            # Use GitLab's global issues endpoint
            issues = self.client.issues.list(**gitlab_filters)

            # Convert to IssueResource objects
            issue_resources = [
                self._convert_to_issue_resource(issue, str(issue.project_id))
                for issue in issues
            ]

            # Apply client-side assignee filtering if needed (for non-current user cases where API filtering failed)
            if (
                assignee_filter
                and assignee_filter != self.username
                and "assignee_id" not in gitlab_filters
            ):
                issue_resources = [
                    issue
                    for issue in issue_resources
                    if issue.assignee == assignee_filter
                ]

            return issue_resources
        except GitlabError as e:
            raise PlatformError(f"Failed to list all issues: {e}", self.platform_name)

    async def get_issue(
        self, project_id: str, issue_id: str
    ) -> Optional[IssueResource]:
        """Get a specific GitLab issue with comments."""
        if not self.client:
            await self.authenticate()

        try:
            project = self.client.projects.get(project_id)
            issue = project.issues.get(issue_id)

            # Get issue comments/notes
            try:
                notes = issue.notes.list(all=True)
                # Filter out system notes (keep only user comments)
                user_comments = [
                    {
                        "id": str(note.id),
                        "author": note.author.get("username")
                        if note.author
                        else "Unknown",
                        "created_at": self._parse_datetime(note.created_at),
                        "updated_at": self._parse_datetime(note.updated_at)
                        if hasattr(note, "updated_at")
                        else None,
                        "body": note.body,
                        "system": getattr(note, "system", False),
                    }
                    for note in notes
                    if not getattr(note, "system", False)  # Only include user comments
                ]
                # Store comments in metadata
                issue_resource = self._convert_to_issue_resource(issue, project_id)
                if not issue_resource.metadata:
                    issue_resource.metadata = {}
                issue_resource.metadata["comments"] = user_comments
                return issue_resource
            except Exception as e:
                # If getting comments fails, still return the issue without comments
                print(f"Warning: Could not fetch comments for issue {issue_id}: {e}")
                return self._convert_to_issue_resource(issue, project_id)

        except GitlabError as e:
            if e.response_code == 404:
                return None
            raise PlatformError(
                f"Failed to get issue {issue_id}: {e}", self.platform_name
            )

    async def create_issue(
        self, project_id: str, title: str, **kwargs
    ) -> IssueResource:
        """Create a new GitLab issue."""
        if not self.client:
            await self.authenticate()

        try:
            project = self.client.projects.get(project_id)
            issue_data = {"title": title, **kwargs}
            issue = project.issues.create(issue_data)
            return self._convert_to_issue_resource(issue, project_id)
        except GitlabError as e:
            raise PlatformError(f"Failed to create issue: {e}", self.platform_name)

    async def update_issue(
        self, project_id: str, issue_id: str, **kwargs
    ) -> IssueResource:
        """Update a GitLab issue."""
        if not self.client:
            await self.authenticate()

        try:
            project = self.client.projects.get(project_id)
            issue = project.issues.get(issue_id)

            for key, value in kwargs.items():
                setattr(issue, key, value)
            issue.save()

            return self._convert_to_issue_resource(issue, project_id)
        except GitlabError as e:
            raise PlatformError(
                f"Failed to update issue {issue_id}: {e}", self.platform_name
            )

    async def close_issue(
        self, project_id: str, issue_id: str, **kwargs
    ) -> IssueResource:
        """Close a GitLab issue."""
        kwargs["state_event"] = "close"
        return await self.update_issue(project_id, issue_id, **kwargs)

    # Merge Request operations
    async def list_merge_requests(
        self, project_id: str, **filters
    ) -> List[MergeRequestResource]:
        """List merge requests for a GitLab project."""
        if not self.client:
            await self.authenticate()

        try:
            project = self.client.projects.get(project_id)
            gitlab_filters = self._normalize_mr_filters(filters)
            mrs = project.mergerequests.list(all=True, **gitlab_filters)

            return [self._convert_to_mr_resource(mr, project_id) for mr in mrs]
        except GitlabError as e:
            raise PlatformError(
                f"Failed to list merge requests: {e}", self.platform_name
            )

    async def get_merge_request(
        self, project_id: str, mr_id: str
    ) -> Optional[MergeRequestResource]:
        """Get a specific GitLab merge request."""
        if not self.client:
            await self.authenticate()

        try:
            project = self.client.projects.get(project_id)
            mr = project.mergerequests.get(mr_id)
            return self._convert_to_mr_resource(mr, project_id)
        except GitlabError as e:
            if e.response_code == 404:
                return None
            raise PlatformError(
                f"Failed to get merge request {mr_id}: {e}", self.platform_name
            )

    async def create_merge_request(
        self,
        project_id: str,
        source_branch: str,
        target_branch: str,
        title: str,
        **kwargs,
    ) -> MergeRequestResource:
        """Create a new GitLab merge request."""
        if not self.client:
            await self.authenticate()

        try:
            project = self.client.projects.get(project_id)
            mr_data = {
                "source_branch": source_branch,
                "target_branch": target_branch,
                "title": title,
            }

            # Handle assignee parameter conversion
            if "assignee_username" in kwargs:
                assignee_username = kwargs.pop("assignee_username")
                try:
                    users = self.client.users.list(username=assignee_username)
                    if users:
                        mr_data["assignee_id"] = users[0].id
                except Exception as e:  # nosec B110
                    # If we can't resolve the username, skip assignee (graceful degradation)
                    print(
                        f"Warning: Could not resolve assignee username '{assignee_username}': {e}"
                    )

            # Add remaining kwargs
            mr_data.update(kwargs)

            mr = project.mergerequests.create(mr_data)
            return self._convert_to_mr_resource(mr, project_id)
        except GitlabError as e:
            raise PlatformError(
                f"Failed to create merge request: {e}", self.platform_name
            )

    async def approve_merge_request(
        self, project_id: str, mr_id: str, **kwargs
    ) -> bool:
        """Approve a GitLab merge request."""
        if not self.client:
            await self.authenticate()

        try:
            project = self.client.projects.get(project_id)
            mr = project.mergerequests.get(mr_id)
            mr.approve(**kwargs)
            return True
        except GitlabError as e:
            raise PlatformError(
                f"Failed to approve merge request {mr_id}: {e}", self.platform_name
            )

    async def merge_merge_request(
        self, project_id: str, mr_id: str, **kwargs
    ) -> MergeRequestResource:
        """Merge a GitLab merge request."""
        if not self.client:
            await self.authenticate()

        try:
            project = self.client.projects.get(project_id)
            mr = project.mergerequests.get(mr_id)
            mr.merge(**kwargs)
            # Refresh the MR to get updated state
            mr = project.mergerequests.get(mr_id)
            return self._convert_to_mr_resource(mr, project_id)
        except GitlabError as e:
            raise PlatformError(
                f"Failed to merge merge request {mr_id}: {e}", self.platform_name
            )

    # Repository operations
    async def list_branches(self, project_id: str, **filters) -> List[Dict[str, Any]]:
        """List branches in a GitLab project."""
        if not self.client:
            await self.authenticate()

        try:
            project = self.client.projects.get(project_id)
            branches = project.branches.list(all=True, **filters)
            return [branch.asdict() for branch in branches]
        except GitlabError as e:
            raise PlatformError(f"Failed to list branches: {e}", self.platform_name)

    async def list_tags(self, project_id: str, **filters) -> List[Dict[str, Any]]:
        """List tags in a GitLab project."""
        if not self.client:
            await self.authenticate()

        try:
            project = self.client.projects.get(project_id)
            tags = project.tags.list(all=True, **filters)
            return [tag.asdict() for tag in tags]
        except GitlabError as e:
            raise PlatformError(f"Failed to list tags: {e}", self.platform_name)

    async def list_commits(self, project_id: str, **filters) -> List[Dict[str, Any]]:
        """List commits in a GitLab project."""
        if not self.client:
            await self.authenticate()

        try:
            project = self.client.projects.get(project_id)
            commits = project.commits.list(all=True, **filters)
            return [commit.asdict() for commit in commits]
        except GitlabError as e:
            raise PlatformError(f"Failed to list commits: {e}", self.platform_name)

    # User operations
    async def get_current_user(self) -> Dict[str, Any]:
        """Get current GitLab user information."""
        if not self.client:
            await self.authenticate()

        try:
            user = self.client.user
            return user.asdict() if hasattr(user, "asdict") else dict(user)
        except GitlabError as e:
            raise PlatformError(f"Failed to get current user: {e}", self.platform_name)

    # Helper methods
    def _convert_to_project_resource(self, project) -> ProjectResource:
        """Convert GitLab project to ProjectResource."""
        return ProjectResource(
            id=str(project.id),
            title=project.name,
            platform=self.platform_name,
            resource_type=ResourceType.PROJECT,
            url=project.web_url,
            namespace=project.path_with_namespace,
            visibility=project.visibility,
            default_branch=getattr(project, "default_branch", None),
            clone_url_http=project.http_url_to_repo,
            clone_url_ssh=project.ssh_url_to_repo,
            description=getattr(project, "description", None),
            created_at=self._parse_datetime(project.created_at),
            updated_at=self._parse_datetime(getattr(project, "last_activity_at", None)),
            metadata=project.asdict() if hasattr(project, "asdict") else dict(project),
        )

    def _convert_to_issue_resource(self, issue, project_id: str) -> IssueResource:
        """Convert GitLab issue to IssueResource."""
        return IssueResource(
            id=str(issue.iid),  # Use internal ID for consistency
            title=issue.title,
            platform=self.platform_name,
            resource_type=ResourceType.ISSUE,
            url=issue.web_url,
            state=ResourceState.OPENED
            if issue.state == "opened"
            else ResourceState.CLOSED,
            project_id=project_id,
            description=getattr(issue, "description", None),
            author=issue.author.get("username") if issue.author else None,
            assignee=issue.assignee.get("username") if issue.assignee else None,
            labels=issue.labels,
            created_at=self._parse_datetime(issue.created_at),
            updated_at=self._parse_datetime(issue.updated_at),
            due_date=self._parse_datetime(getattr(issue, "due_date", None)),
            milestone=issue.milestone.get("title") if issue.milestone else None,
            metadata=issue.asdict() if hasattr(issue, "asdict") else dict(issue),
        )

    def _convert_to_mr_resource(self, mr, project_id: str) -> MergeRequestResource:
        """Convert GitLab merge request to MergeRequestResource."""
        state = ResourceState.OPENED
        if mr.state == "closed":
            state = ResourceState.CLOSED
        elif mr.state == "merged":
            state = ResourceState.MERGED

        return MergeRequestResource(
            id=str(mr.iid),  # Use internal ID for consistency
            title=mr.title,
            platform=self.platform_name,
            resource_type=ResourceType.MERGE_REQUEST,
            url=mr.web_url,
            state=state,
            project_id=project_id,
            source_branch=mr.source_branch,
            target_branch=mr.target_branch,
            description=getattr(mr, "description", None),
            author=mr.author.get("username") if mr.author else None,
            assignee=mr.assignee.get("username") if mr.assignee else None,
            labels=getattr(mr, "labels", []),
            created_at=self._parse_datetime(mr.created_at),
            updated_at=self._parse_datetime(mr.updated_at),
            merge_commit_sha=getattr(mr, "merge_commit_sha", None),
            draft=getattr(mr, "draft", False),
            metadata=mr.asdict() if hasattr(mr, "asdict") else dict(mr),
        )

    def _normalize_project_filters(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize project filters to GitLab format."""
        gitlab_filters = {}

        # Common filter mappings
        filter_mapping = {
            "visibility": "visibility",
            "archived": "archived",
            "owned": "owned",
            "starred": "starred",
            "search": "search",
            "order_by": "order_by",
            "sort": "sort",
        }

        for key, value in filters.items():
            if key in filter_mapping:
                gitlab_filters[filter_mapping[key]] = value

        return gitlab_filters

    def _normalize_issue_filters(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize issue filters to GitLab format."""
        gitlab_filters = {}

        filter_mapping = {
            "state": "state",
            "labels": "labels",
            "assignee": "assignee_username",  # For project-specific searches
            "author": "author_username",  # For project-specific searches
            "milestone": "milestone",
            "order_by": "order_by",
            "sort": "sort",
        }

        for key, value in filters.items():
            if key in filter_mapping:
                gitlab_filters[filter_mapping[key]] = value

        return gitlab_filters

    def _normalize_mr_filters(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize merge request filters to GitLab format."""
        gitlab_filters = {}

        filter_mapping = {
            "state": "state",
            "labels": "labels",
            "assignee": "assignee_username",
            "author": "author_username",
            "milestone": "milestone",
            "source_branch": "source_branch",
            "target_branch": "target_branch",
            "order_by": "order_by",
            "sort": "sort",
        }

        for key, value in filters.items():
            if key in filter_mapping:
                gitlab_filters[filter_mapping[key]] = value

        return gitlab_filters

    def _parse_datetime(self, date_string: Optional[str]) -> Optional[datetime]:
        """Parse GitLab datetime string."""
        if not date_string:
            return None

        try:
            # GitLab uses ISO format: 2024-01-15T10:30:00.000Z
            return datetime.fromisoformat(date_string.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            return None
