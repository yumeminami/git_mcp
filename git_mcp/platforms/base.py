"""Base platform adapter for git-mcp."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from datetime import datetime
from enum import Enum


class ResourceType(Enum):
    """Types of Git platform resources."""

    PROJECT = "project"
    ISSUE = "issue"
    MERGE_REQUEST = "merge_request"
    PULL_REQUEST = "pull_request"  # Alias for merge_request
    USER = "user"
    GROUP = "group"
    BRANCH = "branch"
    TAG = "tag"
    COMMIT = "commit"
    PIPELINE = "pipeline"
    JOB = "job"


class ResourceState(Enum):
    """Common resource states across platforms."""

    OPENED = "opened"
    CLOSED = "closed"
    MERGED = "merged"
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUCCESS = "success"
    FAILED = "failed"
    RUNNING = "running"
    PENDING = "pending"
    CANCELED = "canceled"


@dataclass
class Resource:
    """Generic resource representation across platforms."""

    id: str
    title: str
    platform: str
    resource_type: ResourceType
    url: str
    state: Optional[ResourceState] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    author: Optional[str] = None
    assignee: Optional[str] = None
    labels: Optional[List[str]] = None
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Convert string enum values to enum instances."""
        if isinstance(self.resource_type, str):
            self.resource_type = ResourceType(self.resource_type)
        if isinstance(self.state, str):
            self.state = ResourceState(self.state)


@dataclass
class ProjectResource(Resource):
    """Project-specific resource representation."""

    namespace: Optional[str] = None
    visibility: Optional[str] = None
    default_branch: Optional[str] = None
    clone_url_http: Optional[str] = None
    clone_url_ssh: Optional[str] = None

    def __post_init__(self):
        super().__post_init__()
        self.resource_type = ResourceType.PROJECT


@dataclass
class IssueResource(Resource):
    """Issue-specific resource representation."""

    project_id: Optional[str] = None
    milestone: Optional[str] = None
    due_date: Optional[datetime] = None

    def __post_init__(self):
        super().__post_init__()
        self.resource_type = ResourceType.ISSUE


@dataclass
class MergeRequestResource(Resource):
    """Merge request/Pull request specific resource representation."""

    project_id: Optional[str] = None
    source_branch: Optional[str] = None
    target_branch: Optional[str] = None
    merge_commit_sha: Optional[str] = None
    draft: Optional[bool] = None

    def __post_init__(self):
        super().__post_init__()
        self.resource_type = ResourceType.MERGE_REQUEST


class PlatformAdapter(ABC):
    """Abstract base class for platform adapters."""

    def __init__(
        self, url: str, token: Optional[str] = None, username: Optional[str] = None
    ):
        self.url = url.rstrip("/")
        self.token = token
        self.username = username
        self._authenticated = False

    @property
    @abstractmethod
    def platform_name(self) -> str:
        """Return the platform name (e.g., 'gitlab', 'github')."""
        pass

    @abstractmethod
    async def authenticate(self) -> bool:
        """Authenticate with the platform."""
        pass

    @abstractmethod
    async def test_connection(self) -> bool:
        """Test the connection to the platform."""
        pass

    # Project operations
    @abstractmethod
    async def list_projects(self, **filters) -> List[ProjectResource]:
        """List projects with optional filters."""
        pass

    @abstractmethod
    async def get_project(self, project_id: str) -> Optional[ProjectResource]:
        """Get a specific project by ID."""
        pass

    @abstractmethod
    async def create_project(self, name: str, **kwargs) -> ProjectResource:
        """Create a new project."""
        pass

    @abstractmethod
    async def delete_project(self, project_id: str) -> bool:
        """Delete a project."""
        pass

    # Issue operations
    @abstractmethod
    async def list_issues(self, project_id: str, **filters) -> List[IssueResource]:
        """List issues for a project."""
        pass

    @abstractmethod
    async def list_all_issues(self, **filters) -> List[IssueResource]:
        """List issues across all projects (global search)."""
        pass

    @abstractmethod
    async def get_issue(
        self, project_id: str, issue_id: str
    ) -> Optional[IssueResource]:
        """Get a specific issue."""
        pass

    @abstractmethod
    async def create_issue(
        self, project_id: str, title: str, **kwargs
    ) -> IssueResource:
        """Create a new issue."""
        pass

    @abstractmethod
    async def update_issue(
        self, project_id: str, issue_id: str, **kwargs
    ) -> IssueResource:
        """Update an existing issue."""
        pass

    @abstractmethod
    async def close_issue(
        self, project_id: str, issue_id: str, **kwargs
    ) -> IssueResource:
        """Close an issue."""
        pass

    @abstractmethod
    async def create_issue_comment(
        self, project_id: str, issue_id: str, body: str, **kwargs
    ) -> Dict[str, Any]:
        """Create a comment on an issue."""
        pass

    # Merge Request / Pull Request operations
    @abstractmethod
    async def list_merge_requests(
        self, project_id: str, **filters
    ) -> List[MergeRequestResource]:
        """List merge requests for a project."""
        pass

    @abstractmethod
    async def get_merge_request(
        self, project_id: str, mr_id: str
    ) -> Optional[MergeRequestResource]:
        """Get a specific merge request."""
        pass

    @abstractmethod
    async def create_merge_request(
        self,
        project_id: str,
        source_branch: str,
        target_branch: str,
        title: str,
        **kwargs,
    ) -> MergeRequestResource:
        """Create a new merge request."""
        pass

    @abstractmethod
    async def approve_merge_request(
        self, project_id: str, mr_id: str, **kwargs
    ) -> bool:
        """Approve a merge request."""
        pass

    @abstractmethod
    async def merge_merge_request(
        self, project_id: str, mr_id: str, **kwargs
    ) -> MergeRequestResource:
        """Merge a merge request."""
        pass

    @abstractmethod
    async def close_merge_request(
        self, project_id: str, mr_id: str, **kwargs
    ) -> MergeRequestResource:
        """Close a merge request without merging."""
        pass

    @abstractmethod
    async def update_merge_request(
        self, project_id: str, mr_id: str, **kwargs
    ) -> MergeRequestResource:
        """Update a merge request (title, description, etc.)."""
        pass

    @abstractmethod
    async def get_merge_request_diff(
        self, project_id: str, mr_id: str, **options
    ) -> Dict[str, Any]:
        """Get diff/changes for a merge request."""
        pass

    @abstractmethod
    async def get_merge_request_commits(
        self, project_id: str, mr_id: str, **filters
    ) -> Dict[str, Any]:
        """Get commits for a merge request."""
        pass

    # Repository operations
    @abstractmethod
    async def list_branches(self, project_id: str, **filters) -> List[Dict[str, Any]]:
        """List branches in a project."""
        pass

    @abstractmethod
    async def list_tags(self, project_id: str, **filters) -> List[Dict[str, Any]]:
        """List tags in a project."""
        pass

    @abstractmethod
    async def list_commits(self, project_id: str, **filters) -> List[Dict[str, Any]]:
        """List commits in a project."""
        pass

    # User operations
    @abstractmethod
    async def get_current_user(self) -> Dict[str, Any]:
        """Get current authenticated user information."""
        pass

    # Fork operations
    @abstractmethod
    async def create_fork(self, project_id: str, **kwargs) -> ProjectResource:
        """Create a fork of a repository."""
        pass

    @abstractmethod
    async def is_fork(self, project_id: str) -> bool:
        """Check if a repository is a fork."""
        pass

    @abstractmethod
    async def get_fork_parent(self, project_id: str) -> Optional[str]:
        """Get the parent repository ID of a fork."""
        pass

    @abstractmethod
    def parse_branch_reference(self, branch_ref: str) -> Dict[str, Any]:
        """Parse branch reference into components.

        Args:
            branch_ref: Branch reference in format 'branch' or 'owner:branch'

        Returns:
            Dict with keys: 'owner' (optional), 'branch', 'is_cross_repo'
        """
        pass

    # Utility methods
    def _normalize_filters(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize filter parameters for platform-specific format."""
        return filters

    def _convert_to_resource(
        self, data: Dict[str, Any], resource_type: ResourceType
    ) -> Resource:
        """Convert platform-specific data to generic Resource object."""
        # This is a base implementation, should be overridden by specific adapters
        return Resource(
            id=str(data.get("id", "")),
            title=data.get("title", data.get("name", "")),
            platform=self.platform_name,
            resource_type=resource_type,
            url=data.get("web_url", data.get("html_url", "")),
            metadata=data,
        )

    async def __aenter__(self):
        """Async context manager entry."""
        await self.authenticate()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        # Cleanup if needed
        pass
