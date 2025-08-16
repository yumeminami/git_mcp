"""Comprehensive unit tests for merge request functionality."""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime

from git_mcp.platforms.github import GitHubAdapter
from git_mcp.platforms.gitlab import GitLabAdapter
from git_mcp.platforms.base import ResourceState
from git_mcp.services.platform_service import PlatformService
from git_mcp.core.exceptions import PlatformError
from git_mcp.mcp_server import (
    list_merge_requests,
    get_merge_request_details,
    get_merge_request_diff,
    get_merge_request_commits,
    list_my_merge_requests,
    create_merge_request,
    close_merge_request,
    update_merge_request,
)


class TestGitHubAdapterMROperations:
    """Test GitHub adapter merge request operations."""

    def setup_method(self):
        """Set up test fixtures."""
        self.adapter = GitHubAdapter("https://github.com", "mock-token", "test-user")
        self.mock_client = Mock()
        self.adapter.client = self.mock_client

    @pytest.mark.asyncio
    async def test_list_merge_requests_success(self):
        """Test successful listing of GitHub pull requests."""
        # Arrange
        mock_repo = Mock()
        mock_pr = Mock()

        mock_pr.number = 123
        mock_pr.title = "Test PR"
        mock_pr.state = "open"
        mock_pr.html_url = "https://github.com/owner/repo/pull/123"
        mock_pr.user.login = "test-author"
        mock_pr.created_at = datetime(2025, 8, 16, 12, 0, 0)
        mock_pr.updated_at = datetime(2025, 8, 16, 12, 0, 0)
        mock_pr.head.ref = "feature-branch"
        mock_pr.base.ref = "main"
        mock_pr.labels = []
        mock_pr.assignee = None
        mock_pr.body = "PR description"
        mock_pr.merged = False
        mock_pr.merge_commit_sha = None
        mock_pr.draft = False
        mock_pr.id = 123456
        mock_pr.merged_at = None
        mock_pr.mergeable = True
        mock_pr.mergeable_state = "clean"
        mock_pr.comments = 0
        mock_pr.review_comments = 0
        mock_pr.commits = 1
        mock_pr.additions = 10
        mock_pr.deletions = 5
        mock_pr.changed_files = 1

        self.mock_client.get_repo.return_value = mock_repo
        mock_repo.get_pulls.return_value = [mock_pr]

        # Act
        result = await self.adapter.list_merge_requests(
            "owner/repo", state="open", limit=10
        )

        # Assert
        assert isinstance(result, list)
        assert len(result) == 1

        pr_data = result[0]
        assert pr_data.id == "123"
        assert pr_data.title == "Test PR"
        assert str(pr_data.state) == "ResourceState.OPENED"
        assert pr_data.url == "https://github.com/owner/repo/pull/123"
        assert pr_data.author == "test-author"
        assert pr_data.source_branch == "feature-branch"
        assert pr_data.target_branch == "main"

    @pytest.mark.asyncio
    async def test_get_merge_request_details_success(self):
        """Test successful retrieval of GitHub PR details."""
        # Arrange
        mock_repo = Mock()
        mock_pr = Mock()

        mock_pr.number = 123
        mock_pr.title = "Test PR Details"
        mock_pr.body = "PR description"
        mock_pr.state = "open"
        mock_pr.html_url = "https://github.com/owner/repo/pull/123"
        mock_pr.user.login = "test-author"
        mock_pr.created_at = datetime(2025, 8, 16, 12, 0, 0)
        mock_pr.updated_at = datetime(2025, 8, 16, 12, 0, 0)
        mock_pr.head.ref = "feature-branch"
        mock_pr.base.ref = "main"
        mock_pr.assignee = None
        mock_pr.labels = []
        mock_pr.merged = False
        mock_pr.merge_commit_sha = None
        mock_pr.draft = False
        mock_pr.id = 123456
        mock_pr.merged_at = None
        mock_pr.mergeable = True
        mock_pr.mergeable_state = "clean"
        mock_pr.comments = 0
        mock_pr.review_comments = 0
        mock_pr.commits = 1
        mock_pr.additions = 10
        mock_pr.deletions = 5
        mock_pr.changed_files = 1

        self.mock_client.get_repo.return_value = mock_repo
        mock_repo.get_pull.return_value = mock_pr

        # Act
        result = await self.adapter.get_merge_request("owner/repo", "123")

        # Assert
        assert result.id == "123"
        assert result.title == "Test PR Details"
        assert result.description == "PR description"
        assert result.state == ResourceState.OPENED
        assert result.author == "test-author"

    @pytest.mark.asyncio
    async def test_list_merge_requests_empty_result(self):
        """Test listing PRs when repository has no PRs."""
        # Arrange
        mock_repo = Mock()
        self.mock_client.get_repo.return_value = mock_repo
        mock_repo.get_pulls.return_value = []

        # Act
        result = await self.adapter.list_merge_requests("owner/repo")

        # Assert
        assert isinstance(result, list)
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_list_merge_requests_with_filters(self):
        """Test listing PRs with various filter parameters."""
        # Arrange
        mock_repo = Mock()
        mock_pr = Mock()

        mock_pr.number = 123
        mock_pr.title = "Filtered PR"
        mock_pr.state = "closed"
        mock_pr.html_url = "https://github.com/owner/repo/pull/123"
        mock_pr.user.login = "test-author"
        mock_pr.created_at = datetime(2025, 8, 16, 12, 0, 0)
        mock_pr.updated_at = datetime(2025, 8, 16, 12, 0, 0)
        mock_pr.head.ref = "feature-branch"
        mock_pr.base.ref = "main"
        mock_pr.labels = []
        mock_pr.assignee = None

        self.mock_client.get_repo.return_value = mock_repo
        mock_repo.get_pulls.return_value = [mock_pr]

        # Act
        result = await self.adapter.list_merge_requests(
            "owner/repo", state="closed", limit=5
        )

        # Assert
        assert len(result) == 1
        assert result[0].state == ResourceState.CLOSED

        # Verify that get_pulls was called with correct parameters
        mock_repo.get_pulls.assert_called_once()

    @pytest.mark.asyncio
    async def test_repository_not_found_error(self):
        """Test error handling for non-existent repository."""
        # Arrange
        from github import GithubException

        self.mock_client.get_repo.side_effect = GithubException(404, "Not Found")

        # Act & Assert
        with pytest.raises(PlatformError) as exc_info:
            await self.adapter.list_merge_requests("nonexistent/repo")

        assert "404" in str(exc_info.value)


class TestGitLabAdapterMROperations:
    """Test GitLab adapter merge request operations."""

    def setup_method(self):
        """Set up test fixtures."""
        self.adapter = GitLabAdapter("https://gitlab.com", "mock-token", "test-user")
        self.mock_client = Mock()
        self.adapter.client = Mock()
        self.adapter.client.projects = Mock()

    @pytest.mark.asyncio
    async def test_list_merge_requests_success(self):
        """Test successful listing of GitLab merge requests."""
        # Arrange
        mock_project = Mock()
        mock_mr = Mock()

        mock_mr.iid = 456
        mock_mr.title = "Test MR"
        mock_mr.state = "opened"
        mock_mr.web_url = "https://gitlab.com/group/project/-/merge_requests/456"
        mock_mr.author = {"username": "test-author"}
        mock_mr.created_at = "2025-08-16T12:00:00.000Z"
        mock_mr.updated_at = "2025-08-16T12:00:00.000Z"
        mock_mr.source_branch = "feature-branch"
        mock_mr.target_branch = "main"
        mock_mr.labels = []
        mock_mr.assignee = None

        self.adapter.client.projects.get.return_value = mock_project
        mock_project.mergerequests.list.return_value = [mock_mr]

        # Act
        result = await self.adapter.list_merge_requests(
            "group/project", state="opened", limit=10
        )

        # Assert
        assert isinstance(result, list)
        assert len(result) == 1

        mr_data = result[0]
        assert mr_data.id == "456"
        assert mr_data.title == "Test MR"
        assert mr_data.state == ResourceState.OPENED
        assert mr_data.url == "https://gitlab.com/group/project/-/merge_requests/456"
        assert mr_data.author == "test-author"
        assert mr_data.source_branch == "feature-branch"
        assert mr_data.target_branch == "main"

    @pytest.mark.asyncio
    async def test_get_merge_request_details_success(self):
        """Test successful retrieval of GitLab MR details."""
        # Arrange
        mock_project = Mock()
        mock_mr = Mock()

        mock_mr.iid = 456
        mock_mr.title = "Test MR Details"
        mock_mr.description = "MR description"
        mock_mr.state = "opened"
        mock_mr.web_url = "https://gitlab.com/group/project/-/merge_requests/456"
        mock_mr.author = {"username": "test-author"}
        mock_mr.created_at = "2025-08-16T12:00:00.000Z"
        mock_mr.updated_at = "2025-08-16T12:00:00.000Z"
        mock_mr.source_branch = "feature"
        mock_mr.target_branch = "main"
        mock_mr.assignee = None
        mock_mr.labels = []

        self.adapter.client.projects.get.return_value = mock_project
        mock_project.mergerequests.get.return_value = mock_mr

        # Act
        result = await self.adapter.get_merge_request("group/project", "456")

        # Assert
        assert result.id == "456"
        assert result.title == "Test MR Details"
        assert result.description == "MR description"
        assert result.state == ResourceState.OPENED
        assert result.author == "test-author"

    @pytest.mark.asyncio
    async def test_project_not_found_error(self):
        """Test error handling for non-existent project."""
        # Arrange
        from gitlab import GitlabError

        self.adapter.client.projects.get.side_effect = GitlabError(
            "404 Project Not Found"
        )

        # Act & Assert
        with pytest.raises(PlatformError) as exc_info:
            await self.adapter.list_merge_requests("nonexistent/project")

        assert "404" in str(exc_info.value)


class TestPlatformServiceMRIntegration:
    """Test PlatformService MR operations integration."""

    @pytest.mark.asyncio
    async def test_list_merge_requests_github_routing(self):
        """Test that GitHub requests are routed correctly."""
        with patch.object(PlatformService, "get_adapter") as mock_get_adapter:
            mock_adapter = AsyncMock()
            mock_get_adapter.return_value = mock_adapter
            # Mock a MergeRequestResource-like object
            mock_mr_resource = Mock()
            mock_mr_resource.id = "123"
            mock_mr_resource.title = "Test PR"
            mock_mr_resource.platform = "github"
            mock_adapter.list_merge_requests.return_value = [mock_mr_resource]

            # Act
            result = await PlatformService.list_merge_requests(
                "github", "owner/repo", state="open"
            )

            # Assert
            assert len(result) == 1
            assert result[0]["platform"] == "github"
            mock_adapter.list_merge_requests.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_merge_requests_gitlab_routing(self):
        """Test that GitLab requests are routed correctly."""
        with patch.object(PlatformService, "get_adapter") as mock_get_adapter:
            mock_adapter = AsyncMock()
            mock_get_adapter.return_value = mock_adapter
            # Mock a MergeRequestResource-like object
            mock_mr_resource = Mock()
            mock_mr_resource.id = "456"
            mock_mr_resource.title = "Test MR"
            mock_mr_resource.platform = "gitlab"
            mock_adapter.list_merge_requests.return_value = [mock_mr_resource]

            # Act
            result = await PlatformService.list_merge_requests(
                "gitlab", "group/project", state="opened"
            )

            # Assert
            assert len(result) == 1
            assert result[0]["platform"] == "gitlab"
            mock_adapter.list_merge_requests.assert_called_once()

    @pytest.mark.asyncio
    async def test_unsupported_platform_error(self):
        """Test error handling for unsupported platform."""
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await PlatformService.list_merge_requests(
                "unsupported", "project", state="open"
            )

        assert "Platform 'unsupported' not found" in str(exc_info.value)


class TestMCPToolMRFunctions:
    """Test MCP tool MR functions."""

    @pytest.mark.asyncio
    async def test_list_merge_requests_mcp_tool(self):
        """Test list_merge_requests MCP tool."""
        with patch(
            "git_mcp.mcp_server.PlatformService.list_merge_requests"
        ) as mock_service:
            mock_service.return_value = [
                {"id": "123", "title": "Test PR", "platform": "github"}
            ]

            # Act
            result = await list_merge_requests("github", "owner/repo", state="open")

            # Assert
            assert len(result) == 1
            assert result[0]["id"] == "123"
            mock_service.assert_called_once_with("github", "owner/repo", "open", 20)

    @pytest.mark.asyncio
    async def test_get_merge_request_details_mcp_tool(self):
        """Test get_merge_request_details MCP tool."""
        with patch(
            "git_mcp.mcp_server.PlatformService.get_merge_request_details"
        ) as mock_service:
            mock_service.return_value = {
                "id": "123",
                "title": "Test PR",
                "state": "open",
            }

            # Act
            result = await get_merge_request_details("github", "owner/repo", "123")

            # Assert
            assert result["id"] == "123"
            assert result["title"] == "Test PR"
            mock_service.assert_called_once_with("github", "owner/repo", "123")

    @pytest.mark.asyncio
    async def test_get_merge_request_diff_mcp_tool(self):
        """Test get_merge_request_diff MCP tool."""
        with patch(
            "git_mcp.mcp_server.PlatformService.get_merge_request_diff"
        ) as mock_service:
            mock_service.return_value = {
                "mr_id": "123",
                "files": [],
                "total_changes": {"additions": 0, "deletions": 0},
            }

            # Act
            result = await get_merge_request_diff("github", "owner/repo", "123")

            # Assert
            assert result["mr_id"] == "123"
            assert "files" in result
            mock_service.assert_called_once_with("github", "owner/repo", "123")

    @pytest.mark.asyncio
    async def test_get_merge_request_commits_mcp_tool(self):
        """Test get_merge_request_commits MCP tool."""
        with patch(
            "git_mcp.mcp_server.PlatformService.get_merge_request_commits"
        ) as mock_service:
            mock_service.return_value = {
                "mr_id": "123",
                "commits": [],
                "total_commits": 0,
            }

            # Act
            result = await get_merge_request_commits("github", "owner/repo", "123")

            # Assert
            assert result["mr_id"] == "123"
            assert "commits" in result
            mock_service.assert_called_once_with("github", "owner/repo", "123")

    @pytest.mark.asyncio
    async def test_list_my_merge_requests_mcp_tool(self):
        """Test list_my_merge_requests MCP tool."""
        with patch(
            "git_mcp.mcp_server.PlatformService.list_my_merge_requests"
        ) as mock_service:
            mock_service.return_value = [
                {"id": "123", "title": "My PR", "author": "test-user"}
            ]

            # Act
            result = await list_my_merge_requests("github", "owner/repo", state="open")

            # Assert
            assert len(result) == 1
            assert result[0]["author"] == "test-user"
            mock_service.assert_called_once_with("github", "owner/repo", "open", 20)


class TestMRParameterValidation:
    """Test MR parameter validation and edge cases."""

    @pytest.mark.asyncio
    async def test_list_merge_requests_default_parameters(self):
        """Test list_merge_requests with default parameters."""
        with patch(
            "git_mcp.mcp_server.PlatformService.list_merge_requests"
        ) as mock_service:
            mock_service.return_value = []

            # Act
            await list_merge_requests("github", "owner/repo")

            # Assert
            mock_service.assert_called_once_with("github", "owner/repo", "opened", 20)

    @pytest.mark.asyncio
    async def test_list_merge_requests_custom_limit(self):
        """Test list_merge_requests with custom limit."""
        with patch(
            "git_mcp.mcp_server.PlatformService.list_merge_requests"
        ) as mock_service:
            mock_service.return_value = []

            # Act
            await list_merge_requests("github", "owner/repo", limit=5)

            # Assert
            mock_service.assert_called_once_with("github", "owner/repo", "opened", 5)

    @pytest.mark.asyncio
    async def test_list_merge_requests_all_states(self):
        """Test list_merge_requests with 'all' state."""
        with patch(
            "git_mcp.mcp_server.PlatformService.list_merge_requests"
        ) as mock_service:
            mock_service.return_value = []

            # Act
            await list_merge_requests("github", "owner/repo", state="all")

            # Assert
            mock_service.assert_called_once_with("github", "owner/repo", "all", 20)


class TestMRErrorHandling:
    """Test MR error handling scenarios."""

    @pytest.mark.asyncio
    async def test_platform_service_error_propagation(self):
        """Test that PlatformService errors are properly propagated."""
        with patch(
            "git_mcp.mcp_server.PlatformService.list_merge_requests"
        ) as mock_service:
            mock_service.side_effect = PlatformError("API Error", "test-platform")

            # Act & Assert
            with pytest.raises(PlatformError):
                await list_merge_requests("github", "owner/repo")

    @pytest.mark.asyncio
    async def test_invalid_mr_id_handling(self):
        """Test handling of invalid MR ID."""
        with patch(
            "git_mcp.mcp_server.PlatformService.get_merge_request_details"
        ) as mock_service:
            mock_service.side_effect = PlatformError("MR not found", "test-platform")

            # Act & Assert
            with pytest.raises(PlatformError):
                await get_merge_request_details("github", "owner/repo", "999999")

    @pytest.mark.asyncio
    async def test_network_error_handling(self):
        """Test handling of network errors."""
        with patch(
            "git_mcp.mcp_server.PlatformService.list_merge_requests"
        ) as mock_service:
            mock_service.side_effect = Exception("Network timeout")

            # Act & Assert
            with pytest.raises(Exception):
                await list_merge_requests("github", "owner/repo")


class TestMRDataStructureValidation:
    """Test MR data structure validation."""

    @pytest.mark.asyncio
    async def test_github_mr_data_structure(self):
        """Test GitHub MR data structure consistency."""
        with patch(
            "git_mcp.mcp_server.PlatformService.list_merge_requests"
        ) as mock_service:
            mock_service.return_value = [
                {
                    "id": "123",
                    "title": "Test PR",
                    "state": "open",
                    "url": "https://github.com/owner/repo/pull/123",
                    "author": "test-user",
                    "created_at": "2025-08-16T12:00:00Z",
                    "updated_at": "2025-08-16T12:00:00Z",
                    "source_branch": "feature",
                    "target_branch": "main",
                    "platform": "github",
                    "project_id": "owner/repo",
                }
            ]

            # Act
            result = await list_merge_requests("github", "owner/repo")

            # Assert
            mr = result[0]
            required_fields = [
                "id",
                "title",
                "state",
                "url",
                "author",
                "created_at",
                "updated_at",
                "source_branch",
                "target_branch",
                "platform",
                "project_id",
            ]
            for field in required_fields:
                assert field in mr, f"Missing required field: {field}"

    @pytest.mark.asyncio
    async def test_gitlab_mr_data_structure(self):
        """Test GitLab MR data structure consistency."""
        with patch(
            "git_mcp.mcp_server.PlatformService.list_merge_requests"
        ) as mock_service:
            mock_service.return_value = [
                {
                    "id": "456",
                    "title": "Test MR",
                    "state": "opened",
                    "url": "https://gitlab.com/group/project/-/merge_requests/456",
                    "author": "test-user",
                    "created_at": "2025-08-16T12:00:00Z",
                    "updated_at": "2025-08-16T12:00:00Z",
                    "source_branch": "feature",
                    "target_branch": "main",
                    "platform": "gitlab",
                    "project_id": "group/project",
                }
            ]

            # Act
            result = await list_merge_requests("gitlab", "group/project")

            # Assert
            mr = result[0]
            required_fields = [
                "id",
                "title",
                "state",
                "url",
                "author",
                "created_at",
                "updated_at",
                "source_branch",
                "target_branch",
                "platform",
                "project_id",
            ]
            for field in required_fields:
                assert field in mr, f"Missing required field: {field}"


class TestMRCreateCloseUpdate:
    """Test MR create, close, and update operations."""

    @pytest.mark.asyncio
    async def test_create_merge_request_mcp_tool(self):
        """Test create_merge_request MCP tool."""
        with patch(
            "git_mcp.mcp_server.PlatformService.create_merge_request"
        ) as mock_service:
            mock_service.return_value = {
                "merge_request": {
                    "id": "123",
                    "title": "Test PR",
                    "state": "open",
                    "url": "https://github.com/owner/repo/pull/123",
                },
                "message": "Merge request created successfully",
                "platform": "github",
            }

            # Act
            result = await create_merge_request(
                "github", "owner/repo", "Test PR", "feature", "main", "Test description"
            )

            # Assert
            assert result["merge_request"]["id"] == "123"
            assert result["merge_request"]["title"] == "Test PR"
            assert result["platform"] == "github"
            mock_service.assert_called_once()

    @pytest.mark.asyncio
    async def test_close_merge_request_mcp_tool(self):
        """Test close_merge_request MCP tool."""
        with patch(
            "git_mcp.mcp_server.PlatformService.close_merge_request"
        ) as mock_service:
            mock_service.return_value = {
                "merge_request": {"id": "123", "title": "Test PR", "state": "closed"},
                "message": "Merge request 123 closed successfully",
                "platform": "github",
                "mr_id": "123",
            }

            # Act
            result = await close_merge_request("github", "owner/repo", "123")

            # Assert
            assert result["merge_request"]["state"] == "closed"
            assert result["mr_id"] == "123"
            assert "closed successfully" in result["message"]
            mock_service.assert_called_once_with("github", "owner/repo", "123")

    @pytest.mark.asyncio
    async def test_update_merge_request_mcp_tool(self):
        """Test update_merge_request MCP tool."""
        with patch(
            "git_mcp.mcp_server.PlatformService.update_merge_request"
        ) as mock_service:
            mock_service.return_value = {
                "merge_request": {
                    "id": "123",
                    "title": "Updated Test PR",
                    "state": "open",
                },
                "message": "Merge request 123 updated successfully",
                "platform": "github",
                "mr_id": "123",
            }

            # Act
            result = await update_merge_request(
                "github", "owner/repo", "123", title="Updated Test PR"
            )

            # Assert
            assert result["merge_request"]["title"] == "Updated Test PR"
            assert result["mr_id"] == "123"
            assert "updated successfully" in result["message"]
            mock_service.assert_called_once_with(
                "github", "owner/repo", "123", title="Updated Test PR"
            )


class TestGitHubAdapterCreateCloseUpdate:
    """Test GitHub adapter create, close, and update operations."""

    def setup_method(self):
        """Set up test fixtures."""
        self.adapter = GitHubAdapter("https://github.com", "mock-token", "test-user")
        self.mock_client = Mock()
        self.adapter.client = self.mock_client

    @pytest.mark.asyncio
    async def test_close_merge_request_success(self):
        """Test successful closing of GitHub PR."""
        # Arrange
        mock_repo = Mock()
        mock_pr = Mock()

        mock_pr.number = 123
        mock_pr.title = "Test PR"
        mock_pr.state = "closed"
        mock_pr.html_url = "https://github.com/owner/repo/pull/123"
        mock_pr.user.login = "test-author"
        mock_pr.created_at = datetime(2025, 8, 16, 12, 0, 0)
        mock_pr.updated_at = datetime(2025, 8, 16, 12, 0, 0)
        mock_pr.head.ref = "feature-branch"
        mock_pr.base.ref = "main"
        mock_pr.labels = []
        mock_pr.assignee = None

        self.mock_client.get_repo.return_value = mock_repo
        mock_repo.get_pull.return_value = mock_pr

        # Act
        result = await self.adapter.close_merge_request("owner/repo", "123")

        # Assert
        assert result.id == "123"
        assert result.title == "Test PR"
        assert result.state == ResourceState.CLOSED

        # Verify API calls
        self.mock_client.get_repo.assert_called_once_with("owner/repo")
        mock_repo.get_pull.assert_called_with(123)
        mock_pr.edit.assert_called_once_with(state="closed")

    @pytest.mark.asyncio
    async def test_update_merge_request_success(self):
        """Test successful updating of GitHub PR."""
        # Arrange
        mock_repo = Mock()
        mock_pr = Mock()

        mock_pr.number = 123
        mock_pr.title = "Updated Test PR"
        mock_pr.state = "open"
        mock_pr.html_url = "https://github.com/owner/repo/pull/123"
        mock_pr.user.login = "test-author"
        mock_pr.labels = []
        mock_pr.assignee = None
        mock_pr.body = "New description"
        mock_pr.head.ref = "feature-branch"
        mock_pr.base.ref = "main"
        mock_pr.created_at = datetime(2025, 8, 16, 12, 0, 0)
        mock_pr.updated_at = datetime(2025, 8, 16, 12, 0, 0)
        mock_pr.merged = False
        mock_pr.merge_commit_sha = None
        mock_pr.draft = False
        mock_pr.id = 123456
        mock_pr.merged_at = None
        mock_pr.mergeable = True
        mock_pr.mergeable_state = "clean"
        mock_pr.comments = 0
        mock_pr.review_comments = 0
        mock_pr.commits = 1
        mock_pr.additions = 10
        mock_pr.deletions = 5
        mock_pr.changed_files = 1

        self.mock_client.get_repo.return_value = mock_repo
        mock_repo.get_pull.return_value = mock_pr

        # Act
        result = await self.adapter.update_merge_request(
            "owner/repo", "123", title="Updated Test PR", description="New description"
        )

        # Assert
        assert result.id == "123"
        assert result.title == "Updated Test PR"

        # Verify API calls
        mock_pr.edit.assert_called_once_with(
            title="Updated Test PR", body="New description"
        )


class TestGitLabAdapterCreateCloseUpdate:
    """Test GitLab adapter create, close, and update operations."""

    def setup_method(self):
        """Set up test fixtures."""
        self.adapter = GitLabAdapter("https://gitlab.com", "mock-token", "test-user")
        self.mock_client = Mock()
        self.adapter.client = self.mock_client

    @pytest.mark.asyncio
    async def test_close_merge_request_success(self):
        """Test successful closing of GitLab MR."""
        # Arrange
        mock_project = Mock()
        mock_mr = Mock()

        mock_mr.iid = 456
        mock_mr.title = "Test MR"
        mock_mr.state = "closed"
        mock_mr.web_url = "https://gitlab.com/group/project/-/merge_requests/456"
        mock_mr.author = {"username": "test-author"}
        mock_mr.created_at = "2025-08-16T12:00:00.000Z"
        mock_mr.updated_at = "2025-08-16T12:00:00.000Z"
        mock_mr.source_branch = "feature-branch"
        mock_mr.target_branch = "main"
        mock_mr.labels = []
        mock_mr.assignee = None

        self.mock_client.projects.get.return_value = mock_project
        mock_project.mergerequests.get.return_value = mock_mr

        # Act
        result = await self.adapter.close_merge_request("123", "456")

        # Assert
        assert result.id == "456"
        assert result.title == "Test MR"
        assert result.state == ResourceState.CLOSED

        # Verify API calls
        self.mock_client.projects.get.assert_called_once_with("123")
        mock_project.mergerequests.get.assert_called_with("456")
        assert mock_mr.state_event == "close"
        mock_mr.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_merge_request_success(self):
        """Test successful updating of GitLab MR."""
        # Arrange
        mock_project = Mock()
        mock_mr = Mock()

        mock_mr.iid = 456
        mock_mr.title = "Updated Test MR"
        mock_mr.state = "opened"
        mock_mr.created_at = "2025-08-16T12:00:00.000Z"
        mock_mr.updated_at = "2025-08-16T12:00:00.000Z"
        mock_mr.web_url = "https://gitlab.com/group/project/-/merge_requests/456"
        mock_mr.author = {"username": "test-author"}
        mock_mr.source_branch = "feature"
        mock_mr.target_branch = "main"
        mock_mr.labels = []
        mock_mr.assignee = None
        mock_mr.description = "New description"

        self.mock_client.projects.get.return_value = mock_project
        mock_project.mergerequests.get.return_value = mock_mr

        # Act
        result = await self.adapter.update_merge_request(
            "123", "456", title="Updated Test MR", description="New description"
        )

        # Assert
        assert result.id == "456"
        assert result.title == "Updated Test MR"

        # Verify API calls
        assert mock_mr.title == "Updated Test MR"
        assert mock_mr.description == "New description"
        mock_mr.save.assert_called_once()


class TestPlatformServiceCreateCloseUpdate:
    """Test platform service create, close, and update integration."""

    @pytest.mark.asyncio
    async def test_create_merge_request_service_integration(self):
        """Test service layer integration for create_merge_request."""
        mock_adapter = AsyncMock()
        # Mock a MergeRequestResource-like object
        mock_mr_resource = Mock()
        mock_mr_resource.id = "123"
        mock_mr_resource.title = "Test PR"
        mock_mr_resource.url = "https://github.com/owner/repo/pull/123"
        mock_adapter.create_merge_request.return_value = mock_mr_resource

        with patch.object(PlatformService, "get_adapter", return_value=mock_adapter):
            # Act
            result = await PlatformService.create_merge_request(
                "github", "owner/repo", "Test PR", "feature", "main", description="Test"
            )

            # Assert
            assert result["merge_request"]["id"] == "123"
            assert result["merge_request"]["title"] == "Test PR"
            assert (
                result["merge_request"]["url"]
                == "https://github.com/owner/repo/pull/123"
            )
            assert result["platform"] == "github"
            assert "created successfully" in result["message"]

    @pytest.mark.asyncio
    async def test_close_merge_request_service_integration(self):
        """Test service layer integration for close_merge_request."""
        mock_adapter = AsyncMock()
        # Mock a MergeRequestResource-like object
        mock_mr_resource = Mock()
        mock_mr_resource.id = "123"
        mock_mr_resource.title = "Test PR"
        mock_mr_resource.state = "closed"
        mock_adapter.close_merge_request.return_value = mock_mr_resource

        with patch.object(PlatformService, "get_adapter", return_value=mock_adapter):
            # Act
            result = await PlatformService.close_merge_request(
                "github", "owner/repo", "123"
            )

            # Assert
            assert result["merge_request"].state == "closed"
            assert result["platform"] == "github"
            assert "closed successfully" in result["message"]
            mock_adapter.close_merge_request.assert_called_once_with(
                "owner/repo", "123"
            )


# Test configuration and utilities
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests (fast, isolated)"
    )


if __name__ == "__main__":
    # Run unit tests
    pytest.main([__file__, "-v", "-m", "unit"])
