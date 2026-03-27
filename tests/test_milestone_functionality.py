"""Unit tests for milestone functionality."""

import pytest
from unittest.mock import AsyncMock, Mock, patch, MagicMock
from datetime import datetime

from git_mcp.platforms.github import GitHubAdapter
from git_mcp.platforms.gitlab import GitLabAdapter
from git_mcp.platforms.base import MilestoneResource
from git_mcp.core.exceptions import PlatformError


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_gitlab_milestone(id_=1, title="v1.0", state="active"):
    ms = Mock()
    ms.id = id_
    ms.title = title
    ms.state = state
    ms.description = "First release"
    ms.due_date = "2026-04-01"
    ms.created_at = "2026-01-01T00:00:00.000Z"
    ms.updated_at = "2026-01-02T00:00:00.000Z"
    ms.asdict = lambda: {"id": id_, "title": title}
    return ms


def _make_github_milestone(number=1, title="v1.0", state="open"):
    ms = Mock()
    ms.number = number
    ms.title = title
    ms.state = state
    ms.description = "First release"
    ms.due_on = datetime(2026, 4, 1)
    ms.created_at = datetime(2026, 1, 1)
    ms.updated_at = datetime(2026, 1, 2)
    return ms


# ---------------------------------------------------------------------------
# GitLab milestone tests
# ---------------------------------------------------------------------------


class TestGitLabMilestones:
    def setup_method(self):
        self.adapter = GitLabAdapter("https://gitlab.com", "mock-token", "test-user")
        self.mock_client = Mock()
        self.adapter.client = self.mock_client

    @pytest.mark.asyncio
    async def test_list_milestones(self):
        mock_project = Mock()
        mock_ms = _make_gitlab_milestone()
        self.mock_client.projects.get.return_value = mock_project
        mock_project.milestones.list.return_value = [mock_ms]

        result = await self.adapter.list_milestones("123", state="active")

        assert len(result) == 1
        assert isinstance(result[0], MilestoneResource)
        assert result[0].id == "1"
        assert result[0].title == "v1.0"
        assert result[0].state == "active"
        assert result[0].platform == "gitlab"
        mock_project.milestones.list.assert_called_once_with(state="active", all=True)

    @pytest.mark.asyncio
    async def test_create_milestone(self):
        mock_project = Mock()
        mock_ms = _make_gitlab_milestone()
        self.mock_client.projects.get.return_value = mock_project
        mock_project.milestones.create.return_value = mock_ms

        result = await self.adapter.create_milestone(
            "123", "v1.0", description="First release", due_date="2026-04-01"
        )

        assert isinstance(result, MilestoneResource)
        assert result.title == "v1.0"
        mock_project.milestones.create.assert_called_once_with(
            {"title": "v1.0", "description": "First release", "due_date": "2026-04-01"}
        )

    @pytest.mark.asyncio
    async def test_create_milestone_minimal(self):
        mock_project = Mock()
        mock_ms = _make_gitlab_milestone()
        self.mock_client.projects.get.return_value = mock_project
        mock_project.milestones.create.return_value = mock_ms

        result = await self.adapter.create_milestone("123", "v1.0")

        mock_project.milestones.create.assert_called_once_with({"title": "v1.0"})
        assert result.title == "v1.0"

    @pytest.mark.asyncio
    async def test_update_milestone(self):
        mock_project = Mock()
        mock_ms = _make_gitlab_milestone(title="v1.1")
        self.mock_client.projects.get.return_value = mock_project
        mock_project.milestones.get.return_value = mock_ms

        result = await self.adapter.update_milestone("123", "1", title="v1.1")

        assert result.title == "v1.1"
        mock_ms.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_close_milestone(self):
        mock_project = Mock()
        mock_ms = _make_gitlab_milestone()
        self.mock_client.projects.get.return_value = mock_project
        mock_project.milestones.get.return_value = mock_ms

        result = await self.adapter.close_milestone("123", "1")

        assert result is True
        assert mock_ms.state_event == "close"
        mock_ms.save.assert_called_once()

    def test_resolve_milestone_id_found(self):
        mock_project = Mock()
        mock_ms = _make_gitlab_milestone(id_=42, title="v1.0")
        mock_project.milestones.list.return_value = [mock_ms]

        result = self.adapter._resolve_milestone_id(mock_project, "v1.0")

        assert result == 42

    def test_resolve_milestone_id_not_found(self):
        mock_project = Mock()
        mock_project.milestones.list.return_value = []

        result = self.adapter._resolve_milestone_id(mock_project, "nonexistent")

        assert result is None

    @pytest.mark.asyncio
    async def test_create_issue_with_milestone(self):
        mock_project = Mock()
        mock_ms = _make_gitlab_milestone(id_=5, title="v1.0")
        mock_project.milestones.list.return_value = [mock_ms]

        mock_issue = Mock()
        mock_issue.iid = 1
        mock_issue.title = "Test issue"
        mock_issue.state = "opened"
        mock_issue.web_url = "https://gitlab.com/test/repo/-/issues/1"
        mock_issue.author = {"username": "author"}
        mock_issue.assignee = None
        mock_issue.labels = []
        mock_issue.created_at = "2026-01-01T00:00:00.000Z"
        mock_issue.updated_at = "2026-01-02T00:00:00.000Z"
        mock_issue.description = None
        mock_issue.due_date = None
        mock_issue.milestone = None
        mock_issue.asdict = lambda: {}

        self.mock_client.projects.get.return_value = mock_project
        mock_project.issues.create.return_value = mock_issue

        await self.adapter.create_issue("123", "Test issue", milestone="v1.0")

        call_args = mock_project.issues.create.call_args[0][0]
        assert call_args.get("milestone_id") == 5
        assert "milestone" not in call_args

    @pytest.mark.asyncio
    async def test_create_issue_milestone_not_found_is_ignored(self):
        mock_project = Mock()
        mock_project.milestones.list.return_value = []

        mock_issue = Mock()
        mock_issue.iid = 1
        mock_issue.title = "Test issue"
        mock_issue.state = "opened"
        mock_issue.web_url = "https://gitlab.com/test/repo/-/issues/1"
        mock_issue.author = {"username": "author"}
        mock_issue.assignee = None
        mock_issue.labels = []
        mock_issue.created_at = "2026-01-01T00:00:00.000Z"
        mock_issue.updated_at = "2026-01-02T00:00:00.000Z"
        mock_issue.description = None
        mock_issue.due_date = None
        mock_issue.milestone = None
        mock_issue.asdict = lambda: {}

        self.mock_client.projects.get.return_value = mock_project
        mock_project.issues.create.return_value = mock_issue

        # Should not raise — milestone just gets skipped
        await self.adapter.create_issue("123", "Test issue", milestone="nonexistent")

        call_args = mock_project.issues.create.call_args[0][0]
        assert "milestone_id" not in call_args

    @pytest.mark.asyncio
    async def test_update_issue_with_milestone(self):
        mock_project = Mock()
        mock_ms = _make_gitlab_milestone(id_=7, title="v2.0")
        mock_project.milestones.list.return_value = [mock_ms]

        mock_issue = Mock()
        mock_issue.iid = 1
        mock_issue.title = "Test"
        mock_issue.state = "opened"
        mock_issue.web_url = "https://gitlab.com/test/repo/-/issues/1"
        mock_issue.author = {"username": "author"}
        mock_issue.assignee = None
        mock_issue.labels = []
        mock_issue.created_at = "2026-01-01T00:00:00.000Z"
        mock_issue.updated_at = "2026-01-02T00:00:00.000Z"
        mock_issue.description = None
        mock_issue.due_date = None
        mock_issue.milestone = {"title": "v2.0"}
        mock_issue.asdict = lambda: {}

        self.mock_client.projects.get.return_value = mock_project
        mock_project.issues.get.return_value = mock_issue

        await self.adapter.update_issue("123", "1", milestone="v2.0")

        assert mock_issue.milestone_id == 7
        mock_issue.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_issue_remove_milestone(self):
        mock_project = Mock()
        mock_issue = Mock()
        mock_issue.iid = 1
        mock_issue.title = "Test"
        mock_issue.state = "opened"
        mock_issue.web_url = "https://gitlab.com/test/repo/-/issues/1"
        mock_issue.author = {"username": "author"}
        mock_issue.assignee = None
        mock_issue.labels = []
        mock_issue.created_at = "2026-01-01T00:00:00.000Z"
        mock_issue.updated_at = "2026-01-02T00:00:00.000Z"
        mock_issue.description = None
        mock_issue.due_date = None
        mock_issue.milestone = None
        mock_issue.asdict = lambda: {}

        self.mock_client.projects.get.return_value = mock_project
        mock_project.issues.get.return_value = mock_issue

        await self.adapter.update_issue("123", "1", milestone="")

        assert mock_issue.milestone_id == 0

    def test_convert_to_mr_resource_includes_milestone(self):
        mock_mr = Mock()
        mock_mr.iid = 1
        mock_mr.title = "Test MR"
        mock_mr.state = "opened"
        mock_mr.web_url = "https://gitlab.com/test/repo/-/merge_requests/1"
        mock_mr.source_branch = "feature"
        mock_mr.target_branch = "main"
        mock_mr.author = {"username": "author"}
        mock_mr.assignee = None
        mock_mr.labels = []
        mock_mr.created_at = "2026-01-01T00:00:00.000Z"
        mock_mr.updated_at = "2026-01-02T00:00:00.000Z"
        mock_mr.merge_commit_sha = None
        mock_mr.draft = False
        mock_mr.milestone = {"title": "v1.0"}
        mock_mr.description = None
        mock_mr.asdict = lambda: {}

        resource = self.adapter._convert_to_mr_resource(mock_mr, "123")
        assert resource.milestone == "v1.0"

    def test_convert_to_mr_resource_no_milestone(self):
        mock_mr = Mock()
        mock_mr.iid = 1
        mock_mr.title = "Test MR"
        mock_mr.state = "opened"
        mock_mr.web_url = "https://gitlab.com/test/repo/-/merge_requests/1"
        mock_mr.source_branch = "feature"
        mock_mr.target_branch = "main"
        mock_mr.author = {"username": "author"}
        mock_mr.assignee = None
        mock_mr.labels = []
        mock_mr.created_at = "2026-01-01T00:00:00.000Z"
        mock_mr.updated_at = "2026-01-02T00:00:00.000Z"
        mock_mr.merge_commit_sha = None
        mock_mr.draft = False
        mock_mr.milestone = None
        mock_mr.description = None
        mock_mr.asdict = lambda: {}

        resource = self.adapter._convert_to_mr_resource(mock_mr, "123")
        assert resource.milestone is None


# ---------------------------------------------------------------------------
# GitHub milestone tests
# ---------------------------------------------------------------------------


class TestGitHubMilestones:
    def setup_method(self):
        self.adapter = GitHubAdapter("https://github.com", "mock-token", "test-user")
        self.mock_client = Mock()
        self.adapter.client = self.mock_client

    @pytest.mark.asyncio
    async def test_list_milestones(self):
        mock_repo = Mock()
        mock_ms = _make_github_milestone()
        self.mock_client.get_repo.return_value = mock_repo
        mock_repo.get_milestones.return_value = [mock_ms]

        result = await self.adapter.list_milestones("owner/repo", state="active")

        assert len(result) == 1
        assert isinstance(result[0], MilestoneResource)
        assert result[0].id == "1"
        assert result[0].title == "v1.0"
        assert result[0].state == "active"
        # "active" maps to "open" for GitHub
        mock_repo.get_milestones.assert_called_once_with(state="open")

    @pytest.mark.asyncio
    async def test_list_milestones_closed(self):
        mock_repo = Mock()
        self.mock_client.get_repo.return_value = mock_repo
        mock_repo.get_milestones.return_value = []

        await self.adapter.list_milestones("owner/repo", state="closed")

        mock_repo.get_milestones.assert_called_once_with(state="closed")

    @pytest.mark.asyncio
    async def test_create_milestone(self):
        mock_repo = Mock()
        mock_ms = _make_github_milestone()
        self.mock_client.get_repo.return_value = mock_repo
        mock_repo.create_milestone.return_value = mock_ms

        result = await self.adapter.create_milestone(
            "owner/repo", "v1.0", description="First release", due_date="2026-04-01"
        )

        assert isinstance(result, MilestoneResource)
        assert result.title == "v1.0"
        call_kwargs = mock_repo.create_milestone.call_args
        assert call_kwargs[0][0] == "v1.0"
        assert call_kwargs[1]["description"] == "First release"
        assert "due_on" in call_kwargs[1]

    @pytest.mark.asyncio
    async def test_update_milestone(self):
        mock_repo = Mock()
        mock_ms = _make_github_milestone(title="v1.1")
        self.mock_client.get_repo.return_value = mock_repo
        mock_repo.get_milestone.return_value = mock_ms

        result = await self.adapter.update_milestone(
            "owner/repo", "1", title="v1.1"
        )

        assert result.title == "v1.1"
        mock_ms.edit.assert_called_once_with(title="v1.1")

    @pytest.mark.asyncio
    async def test_close_milestone(self):
        mock_repo = Mock()
        mock_ms = _make_github_milestone()
        self.mock_client.get_repo.return_value = mock_repo
        mock_repo.get_milestone.return_value = mock_ms

        result = await self.adapter.close_milestone("owner/repo", "1")

        assert result is True
        mock_ms.edit.assert_called_once_with(state="closed")

    def test_resolve_milestone_found(self):
        mock_repo = Mock()
        mock_ms = _make_github_milestone(number=3, title="v1.0")
        mock_repo.get_milestones.return_value = [mock_ms]

        result = self.adapter._resolve_milestone(mock_repo, "v1.0")

        assert result is mock_ms

    def test_resolve_milestone_not_found(self):
        mock_repo = Mock()
        mock_repo.get_milestones.return_value = []

        result = self.adapter._resolve_milestone(mock_repo, "nonexistent")

        assert result is None

    @pytest.mark.asyncio
    async def test_create_issue_with_milestone(self):
        mock_repo = Mock()
        mock_ms = _make_github_milestone(number=2, title="v1.0")
        mock_repo.get_milestones.return_value = [mock_ms]

        mock_issue = Mock()
        mock_issue.number = 10
        mock_issue.title = "Test issue"
        mock_issue.state = "open"
        mock_issue.html_url = "https://github.com/owner/repo/issues/10"
        mock_issue.user = Mock(login="author")
        mock_issue.assignee = None
        mock_issue.labels = []
        mock_issue.created_at = datetime(2026, 1, 1)
        mock_issue.updated_at = datetime(2026, 1, 2)
        mock_issue.body = None
        mock_issue.milestone = mock_ms
        mock_issue.locked = False
        mock_issue.comments = 0
        mock_issue.pull_request = None

        self.mock_client.get_repo.return_value = mock_repo
        mock_repo.create_issue.return_value = mock_issue

        await self.adapter.create_issue("owner/repo", "Test issue", milestone="v1.0")

        call_kwargs = mock_repo.create_issue.call_args[1]
        assert call_kwargs.get("milestone") is mock_ms

    @pytest.mark.asyncio
    async def test_update_issue_with_milestone(self):
        mock_repo = Mock()
        mock_ms = _make_github_milestone(number=2, title="v1.0")
        mock_repo.get_milestones.return_value = [mock_ms]

        mock_issue = Mock()
        mock_issue.number = 10
        mock_issue.title = "Test"
        mock_issue.state = "open"
        mock_issue.html_url = "https://github.com/owner/repo/issues/10"
        mock_issue.user = Mock(login="author")
        mock_issue.assignee = None
        mock_issue.labels = []
        mock_issue.created_at = datetime(2026, 1, 1)
        mock_issue.updated_at = datetime(2026, 1, 2)
        mock_issue.body = None
        mock_issue.milestone = mock_ms
        mock_issue.locked = False
        mock_issue.comments = 0
        mock_issue.pull_request = None

        self.mock_client.get_repo.return_value = mock_repo
        mock_repo.get_issue.return_value = mock_issue

        await self.adapter.update_issue("owner/repo", "10", milestone="v1.0")

        call_kwargs = mock_issue.edit.call_args[1]
        assert call_kwargs.get("milestone") is mock_ms

    @pytest.mark.asyncio
    async def test_update_issue_remove_milestone(self):
        mock_repo = Mock()
        mock_issue = Mock()
        mock_issue.number = 10
        mock_issue.title = "Test"
        mock_issue.state = "open"
        mock_issue.html_url = "https://github.com/owner/repo/issues/10"
        mock_issue.user = Mock(login="author")
        mock_issue.assignee = None
        mock_issue.labels = []
        mock_issue.created_at = datetime(2026, 1, 1)
        mock_issue.updated_at = datetime(2026, 1, 2)
        mock_issue.body = None
        mock_issue.milestone = None
        mock_issue.locked = False
        mock_issue.comments = 0
        mock_issue.pull_request = None

        self.mock_client.get_repo.return_value = mock_repo
        mock_repo.get_issue.return_value = mock_issue

        await self.adapter.update_issue("owner/repo", "10", milestone="")

        call_kwargs = mock_issue.edit.call_args[1]
        assert call_kwargs.get("milestone") is None

    def test_convert_to_mr_resource_includes_milestone(self):
        mock_pr = Mock()
        mock_pr.number = 5
        mock_pr.title = "Test PR"
        mock_pr.state = "open"
        mock_pr.html_url = "https://github.com/owner/repo/pull/5"
        mock_pr.head = Mock(ref="feature")
        mock_pr.base = Mock(ref="main")
        mock_pr.user = Mock(login="author")
        mock_pr.assignee = None
        mock_pr.labels = []
        mock_pr.created_at = datetime(2026, 1, 1)
        mock_pr.updated_at = datetime(2026, 1, 2)
        mock_pr.body = None
        mock_pr.merged = False
        mock_pr.merge_commit_sha = None
        mock_pr.draft = False
        mock_pr.id = 999
        mock_pr.merged_at = None
        mock_pr.mergeable = True
        mock_pr.mergeable_state = "clean"
        mock_pr.comments = 0
        mock_pr.review_comments = 0
        mock_pr.commits = 1
        mock_pr.additions = 5
        mock_pr.deletions = 2
        mock_pr.changed_files = 1
        mock_pr.milestone = Mock(title="v1.0")

        resource = self.adapter._convert_to_mr_resource(mock_pr, "owner/repo")
        assert resource.milestone == "v1.0"

    def test_convert_to_mr_resource_no_milestone(self):
        mock_pr = Mock()
        mock_pr.number = 5
        mock_pr.title = "Test PR"
        mock_pr.state = "open"
        mock_pr.html_url = "https://github.com/owner/repo/pull/5"
        mock_pr.head = Mock(ref="feature")
        mock_pr.base = Mock(ref="main")
        mock_pr.user = Mock(login="author")
        mock_pr.assignee = None
        mock_pr.labels = []
        mock_pr.created_at = datetime(2026, 1, 1)
        mock_pr.updated_at = datetime(2026, 1, 2)
        mock_pr.body = None
        mock_pr.merged = False
        mock_pr.merge_commit_sha = None
        mock_pr.draft = False
        mock_pr.id = 999
        mock_pr.merged_at = None
        mock_pr.mergeable = True
        mock_pr.mergeable_state = "clean"
        mock_pr.comments = 0
        mock_pr.review_comments = 0
        mock_pr.commits = 1
        mock_pr.additions = 5
        mock_pr.deletions = 2
        mock_pr.changed_files = 1
        mock_pr.milestone = None

        resource = self.adapter._convert_to_mr_resource(mock_pr, "owner/repo")
        assert resource.milestone is None


# ---------------------------------------------------------------------------
# MCP tool tests (service layer)
# ---------------------------------------------------------------------------


class TestMilestoneMCPTools:
    @pytest.mark.asyncio
    async def test_list_milestones_mcp_tool(self):
        from git_mcp.mcp_server import list_milestones

        with patch("git_mcp.services.platform_service.PlatformService.list_milestones") as mock_svc:
            mock_svc.return_value = [
                {
                    "id": "1",
                    "title": "v1.0",
                    "state": "active",
                    "platform": "gitlab",
                    "project_id": "123",
                }
            ]
            result = await list_milestones("gitlab", "123")
            assert len(result) == 1
            assert result[0]["title"] == "v1.0"
            mock_svc.assert_called_once_with("gitlab", "123", "active")

    @pytest.mark.asyncio
    async def test_create_milestone_mcp_tool(self):
        from git_mcp.mcp_server import create_milestone

        with patch("git_mcp.services.platform_service.PlatformService.create_milestone") as mock_svc:
            mock_svc.return_value = {
                "id": "1",
                "title": "v1.0",
                "message": "Milestone 'v1.0' created successfully",
            }
            result = await create_milestone("gitlab", "123", "v1.0", due_date="2026-04-01")
            assert result["title"] == "v1.0"
            mock_svc.assert_called_once_with("gitlab", "123", "v1.0", None, "2026-04-01")

    @pytest.mark.asyncio
    async def test_update_milestone_mcp_tool(self):
        from git_mcp.mcp_server import update_milestone

        with patch("git_mcp.services.platform_service.PlatformService.update_milestone") as mock_svc:
            mock_svc.return_value = {"id": "1", "title": "v1.1"}
            result = await update_milestone("gitlab", "123", "1", title="v1.1")
            assert result["title"] == "v1.1"
            mock_svc.assert_called_once_with("gitlab", "123", "1", title="v1.1")

    @pytest.mark.asyncio
    async def test_close_milestone_mcp_tool(self):
        from git_mcp.mcp_server import close_milestone

        with patch("git_mcp.services.platform_service.PlatformService.close_milestone") as mock_svc:
            mock_svc.return_value = {"milestone_id": "1", "message": "Milestone '1' closed successfully"}
            result = await close_milestone("gitlab", "123", "1")
            assert "closed successfully" in result["message"]
            mock_svc.assert_called_once_with("gitlab", "123", "1")

    @pytest.mark.asyncio
    async def test_create_issue_with_milestone_mcp_tool(self):
        from git_mcp.mcp_server import create_issue

        with patch("git_mcp.services.platform_service.PlatformService.create_issue") as mock_svc:
            mock_svc.return_value = {
                "id": "1",
                "title": "My issue",
                "state": "opened",
                "url": "https://gitlab.com/test/repo/-/issues/1",
            }
            result = await create_issue("gitlab", "123", "My issue", milestone="v1.0")
            mock_svc.assert_called_once_with(
                "gitlab", "123", "My issue", None, None, None, "v1.0"
            )

    @pytest.mark.asyncio
    async def test_update_issue_with_milestone_mcp_tool(self):
        from git_mcp.mcp_server import update_issue

        with patch("git_mcp.services.platform_service.PlatformService.update_issue") as mock_svc:
            mock_svc.return_value = {"id": "1", "title": "My issue", "state": "opened"}
            await update_issue("gitlab", "123", "1", milestone="v1.0")
            call_kwargs = mock_svc.call_args[1]
            assert call_kwargs.get("milestone") == "v1.0"
