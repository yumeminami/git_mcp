"""Comprehensive tests for issue comment functionality."""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime

from git_mcp.platforms.github import GitHubAdapter
from git_mcp.platforms.gitlab import GitLabAdapter
from git_mcp.services.platform_service import PlatformService
from git_mcp.core.exceptions import PlatformError
from git_mcp.mcp_server import create_issue_comment


class TestGitHubAdapterCommentCreation:
    """Test GitHub adapter comment creation functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.adapter = GitHubAdapter("https://github.com", "mock-token", "test-user")
        self.mock_client = Mock()
        self.adapter.client = self.mock_client

    @pytest.mark.asyncio
    async def test_create_comment_success(self):
        """Test successful comment creation on GitHub."""
        # Arrange
        mock_repo = Mock()
        mock_issue = Mock()
        mock_comment = Mock()

        mock_comment.id = 123456789
        mock_comment.user.login = "test-user"
        mock_comment.created_at = datetime(2025, 8, 15, 12, 0, 0)
        mock_comment.updated_at = datetime(2025, 8, 15, 12, 0, 0)
        mock_comment.body = "Test comment body"
        mock_comment.html_url = (
            "https://github.com/owner/repo/issues/1#issuecomment-123456789"
        )

        self.mock_client.get_repo.return_value = mock_repo
        mock_repo.get_issue.return_value = mock_issue
        mock_issue.create_comment.return_value = mock_comment

        # Act
        result = await self.adapter.create_issue_comment(
            "owner/repo", "1", "Test comment body"
        )

        # Assert
        assert result == {
            "id": "123456789",
            "author": "test-user",
            "created_at": "2025-08-15T12:00:00",
            "updated_at": "2025-08-15T12:00:00",
            "body": "Test comment body",
            "url": "https://github.com/owner/repo/issues/1#issuecomment-123456789",
        }

        # Verify API calls
        self.mock_client.get_repo.assert_called_once_with("owner/repo")
        mock_repo.get_issue.assert_called_once_with(1)
        mock_issue.create_comment.assert_called_once_with("Test comment body")

    @pytest.mark.asyncio
    async def test_create_comment_missing_user(self):
        """Test comment creation when user info is missing."""
        # Arrange
        mock_repo = Mock()
        mock_issue = Mock()
        mock_comment = Mock()

        mock_comment.id = 123456789
        mock_comment.user = None  # Missing user
        mock_comment.created_at = None
        mock_comment.updated_at = None
        mock_comment.body = "Test comment body"

        self.mock_client.get_repo.return_value = mock_repo
        mock_repo.get_issue.return_value = mock_issue
        mock_issue.create_comment.return_value = mock_comment

        # Act
        result = await self.adapter.create_issue_comment(
            "owner/repo", "1", "Test comment body"
        )

        # Assert
        assert result["author"] == "Unknown"
        assert result["created_at"] is None
        assert result["updated_at"] is None

    @pytest.mark.asyncio
    async def test_create_comment_authentication_required(self):
        """Test that authentication is called when client is not available."""
        # Arrange
        self.adapter.client = None
        self.adapter.authenticate = AsyncMock()

        mock_repo = Mock()
        mock_issue = Mock()
        mock_comment = Mock()
        mock_comment.id = 123
        mock_comment.user.login = "test-user"
        mock_comment.body = "Test"

        # Mock the client after authentication
        mock_client = Mock()
        mock_client.get_repo.return_value = mock_repo
        mock_repo.get_issue.return_value = mock_issue
        mock_issue.create_comment.return_value = mock_comment

        async def mock_auth():
            self.adapter.client = mock_client

        self.adapter.authenticate.side_effect = mock_auth

        # Act
        await self.adapter.create_issue_comment("owner/repo", "1", "Test")

        # Assert
        self.adapter.authenticate.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_comment_github_exception(self):
        """Test handling of GitHub API exceptions."""
        # Arrange
        from github import GithubException

        mock_repo = Mock()
        self.mock_client.get_repo.return_value = mock_repo
        mock_repo.get_issue.side_effect = GithubException(404, "Not Found", {})

        # Act & Assert
        with pytest.raises(PlatformError) as exc_info:
            await self.adapter.create_issue_comment("owner/repo", "999", "Test")

        assert "Failed to create comment" in str(exc_info.value)
        assert exc_info.value.platform == "github"

    @pytest.mark.asyncio
    async def test_create_comment_invalid_issue_id(self):
        """Test handling of invalid issue ID conversion."""
        # Arrange
        mock_repo = Mock()
        self.mock_client.get_repo.return_value = mock_repo
        mock_repo.get_issue.side_effect = ValueError("invalid literal for int()")

        # Act & Assert
        with pytest.raises(ValueError):
            await self.adapter.create_issue_comment("owner/repo", "invalid", "Test")


class TestGitLabAdapterCommentCreation:
    """Test GitLab adapter comment creation functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.adapter = GitLabAdapter("https://gitlab.com", "mock-token", "test-user")
        self.mock_client = Mock()
        self.adapter.client = self.mock_client

    @pytest.mark.asyncio
    async def test_create_comment_success(self):
        """Test successful comment creation on GitLab."""
        # Arrange
        mock_project = Mock()
        mock_issue = Mock()
        mock_note = Mock()

        mock_note.id = 987654321
        mock_note.author.username = "test-user"
        mock_note.created_at = "2025-08-15T12:00:00.000Z"
        mock_note.updated_at = "2025-08-15T12:00:00.000Z"
        mock_note.body = "Test GitLab comment"
        mock_note.web_url = "https://gitlab.com/owner/repo/-/issues/1#note_987654321"

        self.mock_client.projects.get.return_value = mock_project
        mock_project.issues.get.return_value = mock_issue
        mock_issue.notes.create.return_value = mock_note

        # Act
        result = await self.adapter.create_issue_comment(
            "123", "1", "Test GitLab comment"
        )

        # Assert
        assert result == {
            "id": "987654321",
            "author": "test-user",
            "created_at": "2025-08-15T12:00:00.000Z",
            "updated_at": "2025-08-15T12:00:00.000Z",
            "body": "Test GitLab comment",
            "url": "https://gitlab.com/owner/repo/-/issues/1#note_987654321",
        }

        # Verify API calls
        self.mock_client.projects.get.assert_called_once_with("123")
        mock_project.issues.get.assert_called_once_with("1")
        mock_issue.notes.create.assert_called_once_with({"body": "Test GitLab comment"})

    @pytest.mark.asyncio
    async def test_create_comment_missing_author(self):
        """Test comment creation when author info is missing."""
        # Arrange
        mock_project = Mock()
        mock_issue = Mock()
        mock_note = Mock()

        mock_note.id = 987654321
        del mock_note.author  # Missing author
        mock_note.created_at = "2025-08-15T12:00:00.000Z"
        mock_note.updated_at = "2025-08-15T12:00:00.000Z"
        mock_note.body = "Test comment"

        self.mock_client.projects.get.return_value = mock_project
        mock_project.issues.get.return_value = mock_issue
        mock_issue.notes.create.return_value = mock_note

        # Act
        result = await self.adapter.create_issue_comment("123", "1", "Test comment")

        # Assert
        assert result["author"] == "Unknown"

    @pytest.mark.asyncio
    async def test_create_comment_authentication_required(self):
        """Test that authentication is called when client is not available."""
        # Arrange
        self.adapter.client = None
        self.adapter.authenticate = AsyncMock()

        mock_project = Mock()
        mock_issue = Mock()
        mock_note = Mock()
        mock_note.id = 123
        mock_note.body = "Test"

        # Mock the client after authentication
        mock_client = Mock()
        mock_client.projects.get.return_value = mock_project
        mock_project.issues.get.return_value = mock_issue
        mock_issue.notes.create.return_value = mock_note

        async def mock_auth():
            self.adapter.client = mock_client

        self.adapter.authenticate.side_effect = mock_auth

        # Act
        await self.adapter.create_issue_comment("123", "1", "Test")

        # Assert
        self.adapter.authenticate.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_comment_gitlab_exception(self):
        """Test handling of GitLab API exceptions."""
        # Arrange
        from gitlab.exceptions import GitlabError

        mock_project = Mock()
        self.mock_client.projects.get.return_value = mock_project
        mock_project.issues.get.side_effect = GitlabError("Issue not found")

        # Act & Assert
        with pytest.raises(PlatformError) as exc_info:
            await self.adapter.create_issue_comment("123", "999", "Test")

        assert "Failed to create comment" in str(exc_info.value)
        assert exc_info.value.platform == "gitlab"


class TestPlatformServiceCommentCreation:
    """Test platform service comment creation integration."""

    @pytest.mark.asyncio
    async def test_create_comment_github_integration(self):
        """Test service layer integration with GitHub adapter."""
        # Arrange
        mock_adapter = AsyncMock()
        mock_adapter.create_issue_comment.return_value = {
            "id": "123",
            "author": "test-user",
            "created_at": "2025-08-15T12:00:00",
            "updated_at": "2025-08-15T12:00:00",
            "body": "Test comment",
            "url": "https://github.com/owner/repo/issues/1#issuecomment-123",
        }

        with patch.object(PlatformService, "get_adapter", return_value=mock_adapter):
            # Act
            result = await PlatformService.create_issue_comment(
                "github", "owner/repo", "1", "Test comment"
            )

            # Assert
            assert result["comment"]["id"] == "123"
            assert result["issue_id"] == "1"
            assert result["project_id"] == "owner/repo"
            assert result["platform"] == "github"
            assert result["message"] == "Comment created successfully on issue 1"

            mock_adapter.create_issue_comment.assert_called_once_with(
                "owner/repo", "1", "Test comment"
            )

    @pytest.mark.asyncio
    async def test_create_comment_gitlab_integration(self):
        """Test service layer integration with GitLab adapter."""
        # Arrange
        mock_adapter = AsyncMock()
        mock_adapter.create_issue_comment.return_value = {
            "id": "456",
            "author": "gitlab-user",
            "created_at": "2025-08-15T12:00:00.000Z",
            "updated_at": "2025-08-15T12:00:00.000Z",
            "body": "GitLab test comment",
            "url": "https://gitlab.com/owner/repo/-/issues/1#note_456",
        }

        with patch.object(PlatformService, "get_adapter", return_value=mock_adapter):
            # Act
            result = await PlatformService.create_issue_comment(
                "gitlab", "123", "1", "GitLab test comment"
            )

            # Assert
            assert result["comment"]["id"] == "456"
            assert result["issue_id"] == "1"
            assert result["project_id"] == "123"
            assert result["platform"] == "gitlab"

    @pytest.mark.asyncio
    async def test_create_comment_with_kwargs(self):
        """Test service layer with additional keyword arguments."""
        # Arrange
        mock_adapter = AsyncMock()
        mock_adapter.create_issue_comment.return_value = {"id": "789"}

        with patch.object(PlatformService, "get_adapter", return_value=mock_adapter):
            # Act
            await PlatformService.create_issue_comment(
                "github", "owner/repo", "1", "Test", custom_param="value"
            )

            # Assert
            mock_adapter.create_issue_comment.assert_called_once_with(
                "owner/repo", "1", "Test", custom_param="value"
            )

    @pytest.mark.asyncio
    async def test_create_comment_adapter_error_propagation(self):
        """Test that adapter errors are properly propagated."""
        # Arrange
        mock_adapter = AsyncMock()
        mock_adapter.create_issue_comment.side_effect = PlatformError(
            "API Error", "github"
        )

        with patch.object(PlatformService, "get_adapter", return_value=mock_adapter):
            # Act & Assert
            with pytest.raises(PlatformError):
                await PlatformService.create_issue_comment(
                    "github", "owner/repo", "1", "Test"
                )


class TestMCPToolIntegration:
    """Test MCP tool integration for comment creation."""

    @pytest.mark.asyncio
    async def test_mcp_tool_success(self):
        """Test successful MCP tool execution."""
        # Arrange
        expected_result = {
            "comment": {"id": "123", "author": "test-user"},
            "issue_id": "1",
            "project_id": "owner/repo",
            "platform": "github",
            "message": "Comment created successfully on issue 1",
        }

        with patch.object(
            PlatformService, "create_issue_comment", return_value=expected_result
        ) as mock_service:
            # Act
            result = await create_issue_comment(
                "github", "owner/repo", "1", "Test comment"
            )

            # Assert
            assert result == expected_result
            mock_service.assert_called_once_with(
                "github", "owner/repo", "1", "Test comment"
            )

    @pytest.mark.asyncio
    async def test_mcp_tool_with_kwargs(self):
        """Test MCP tool with additional parameters."""
        # Arrange
        expected_result = {"comment": {"id": "456"}}

        with patch.object(
            PlatformService, "create_issue_comment", return_value=expected_result
        ) as mock_service:
            # Act
            result = await create_issue_comment(
                "gitlab", "123", "1", "Test", extra_param="value"
            )

            # Assert
            assert result == expected_result
            mock_service.assert_called_once_with(
                "gitlab", "123", "1", "Test", extra_param="value"
            )

    @pytest.mark.asyncio
    async def test_mcp_tool_error_handling(self):
        """Test MCP tool error handling."""
        # Arrange
        with patch.object(
            PlatformService,
            "create_issue_comment",
            side_effect=PlatformError("Test error", "github"),
        ):
            # Act & Assert
            with pytest.raises(PlatformError):
                await create_issue_comment("github", "owner/repo", "1", "Test")


class TestErrorScenarios:
    """Test various error scenarios and edge cases."""

    @pytest.mark.asyncio
    async def test_empty_comment_body(self):
        """Test comment creation with empty body."""
        adapter = GitHubAdapter("https://github.com", "token", "user")
        adapter.client = Mock()

        mock_repo = Mock()
        mock_issue = Mock()
        mock_comment = Mock()
        mock_comment.id = 123
        mock_comment.body = ""

        adapter.client.get_repo.return_value = mock_repo
        mock_repo.get_issue.return_value = mock_issue
        mock_issue.create_comment.return_value = mock_comment

        # Act
        result = await adapter.create_issue_comment("owner/repo", "1", "")

        # Assert
        assert result["body"] == ""
        mock_issue.create_comment.assert_called_once_with("")

    @pytest.mark.asyncio
    async def test_long_comment_body(self):
        """Test comment creation with very long body."""
        adapter = GitHubAdapter("https://github.com", "token", "user")
        adapter.client = Mock()

        long_body = "x" * 10000  # Very long comment

        mock_repo = Mock()
        mock_issue = Mock()
        mock_comment = Mock()
        mock_comment.id = 123
        mock_comment.body = long_body

        adapter.client.get_repo.return_value = mock_repo
        mock_repo.get_issue.return_value = mock_issue
        mock_issue.create_comment.return_value = mock_comment

        # Act
        result = await adapter.create_issue_comment("owner/repo", "1", long_body)

        # Assert
        assert result["body"] == long_body

    @pytest.mark.asyncio
    async def test_special_characters_in_comment(self):
        """Test comment creation with special characters."""
        adapter = GitHubAdapter("https://github.com", "token", "user")
        adapter.client = Mock()

        special_body = "Comment with 🚀 emojis and @mentions #hashtags **markdown**"

        mock_repo = Mock()
        mock_issue = Mock()
        mock_comment = Mock()
        mock_comment.id = 123
        mock_comment.body = special_body

        adapter.client.get_repo.return_value = mock_repo
        mock_repo.get_issue.return_value = mock_issue
        mock_issue.create_comment.return_value = mock_comment

        # Act
        result = await adapter.create_issue_comment("owner/repo", "1", special_body)

        # Assert
        assert result["body"] == special_body

    @pytest.mark.asyncio
    async def test_nonexistent_platform(self):
        """Test service layer with nonexistent platform."""
        with patch.object(
            PlatformService,
            "get_adapter",
            side_effect=ValueError("Platform 'nonexistent' not found"),
        ):
            # Act & Assert
            with pytest.raises(ValueError):
                await PlatformService.create_issue_comment(
                    "nonexistent", "owner/repo", "1", "Test"
                )


class TestRealWorldIntegration:
    """Integration tests that could be run against real APIs (with proper setup)."""

    @pytest.mark.integration
    @pytest.mark.skip(reason="Requires real API credentials and test issues")
    @pytest.mark.asyncio
    async def test_github_real_comment_creation(self):
        """Test comment creation on real GitHub issue (requires setup)."""
        # This test would require:
        # 1. Real GitHub token in environment
        # 2. Access to test repository
        # 3. Test issue that can receive comments

        # Example implementation:
        # adapter = GitHubAdapter("https://github.com", os.getenv("GITHUB_TOKEN"), "test-user")
        # result = await adapter.create_issue_comment("yumeminami/git_mcp", "29", "Integration test comment")
        # assert result["id"] is not None
        pass

    @pytest.mark.integration
    @pytest.mark.skip(reason="Requires real API credentials and test issues")
    @pytest.mark.asyncio
    async def test_gitlab_real_comment_creation(self):
        """Test comment creation on real GitLab issue (requires setup)."""
        # This test would require:
        # 1. Real GitLab token in environment
        # 2. Access to test project
        # 3. Test issue that can receive comments
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
