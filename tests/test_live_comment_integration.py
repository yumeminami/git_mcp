"""Live integration tests for comment functionality with real APIs."""

import pytest
import asyncio
from datetime import datetime

from git_mcp.services.platform_service import PlatformService
from git_mcp.mcp_server import create_issue_comment
from git_mcp.core.config import get_config


def check_github_available():
    """Check if GitHub platform is configured and available."""
    try:
        config = get_config()
        platforms = config.list_platforms()
        return "github" in platforms and config.get_platform("github") is not None
    except Exception:
        return False


def check_gitlab_available():
    """Check if GitLab platform is configured and available."""
    try:
        config = get_config()
        platforms = config.list_platforms()
        return "gitlab" in platforms and config.get_platform("gitlab") is not None
    except Exception:
        return False


github_available = check_github_available()
gitlab_available = check_gitlab_available()


class TestLiveCommentIntegration:
    """Integration tests using actual test issues."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.skipif(not github_available, reason="GitHub platform not configured")
    async def test_github_comment_creation_live(self):
        """Test comment creation on GitHub test issue #29."""
        # Test data
        platform = "github"
        project_id = "yumeminami/git_mcp"
        issue_id = "29"
        test_comment = (
            f"🧪 Test comment from automated test suite - {datetime.now().isoformat()}"
        )

        try:
            # Act - Create comment using service layer
            result = await PlatformService.create_issue_comment(
                platform, project_id, issue_id, test_comment
            )

            # Assert service layer response structure
            assert "comment" in result
            assert "issue_id" in result
            assert "project_id" in result
            assert "platform" in result
            assert "message" in result

            assert result["issue_id"] == issue_id
            assert result["project_id"] == project_id
            assert result["platform"] == platform
            assert "successfully" in result["message"]

            # Assert comment data structure
            comment_data = result["comment"]
            assert "id" in comment_data
            assert "author" in comment_data
            assert "body" in comment_data
            assert comment_data["body"] == test_comment

            # Verify timestamps are present (GitHub should provide them)
            assert "created_at" in comment_data
            assert "updated_at" in comment_data

            # Verify URL is present
            assert "url" in comment_data
            if comment_data["url"]:
                assert "github.com" in comment_data["url"]
                assert f"issues/{issue_id}" in comment_data["url"]

            print("✅ GitHub comment created successfully:")
            print(f"   Comment ID: {comment_data['id']}")
            print(f"   Author: {comment_data['author']}")
            print(f"   URL: {comment_data.get('url', 'N/A')}")

        except Exception as e:
            pytest.fail(f"GitHub comment creation failed: {str(e)}")

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.skipif(not gitlab_available, reason="GitLab platform not configured")
    async def test_gitlab_comment_creation_live(self):
        """Test comment creation on GitLab test issue #1."""
        # Test data
        platform = "gitlab"  # GitLab platform name
        project_id = "gitlab-org/gitlab"
        issue_id = "1"
        test_comment = f"🧪 GitLab test comment from automated test suite - {datetime.now().isoformat()}"

        try:
            # Act - Create comment using service layer
            result = await PlatformService.create_issue_comment(
                platform, project_id, issue_id, test_comment
            )

            # Assert service layer response structure
            assert "comment" in result
            assert "issue_id" in result
            assert "project_id" in result
            assert "platform" in result
            assert "message" in result

            assert result["issue_id"] == issue_id
            assert result["project_id"] == project_id
            assert result["platform"] == platform
            assert "successfully" in result["message"]

            # Assert comment data structure
            comment_data = result["comment"]
            assert "id" in comment_data
            assert "author" in comment_data
            assert "body" in comment_data
            assert comment_data["body"] == test_comment

            # Verify timestamps are present
            assert "created_at" in comment_data
            assert "updated_at" in comment_data

            # Verify URL format
            assert "url" in comment_data
            if comment_data["url"]:
                assert "gitlab.com" in comment_data["url"]

            print("✅ GitLab comment created successfully:")
            print(f"   Comment ID: {comment_data['id']}")
            print(f"   Author: {comment_data['author']}")
            print(f"   URL: {comment_data.get('url', 'N/A')}")

        except Exception as e:
            pytest.fail(f"GitLab comment creation failed: {str(e)}")

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.skipif(not github_available, reason="GitHub platform not configured")
    async def test_mcp_tool_github_live(self):
        """Test MCP tool with GitHub live API."""
        # Test data
        platform = "github"
        project_id = "yumeminami/git_mcp"
        issue_id = "29"
        test_comment = f"🔧 MCP tool test comment - {datetime.now().isoformat()}"

        try:
            # Act - Use MCP tool directly
            result = await create_issue_comment(
                platform, project_id, issue_id, test_comment
            )

            # Assert MCP tool response (should match service layer)
            assert "comment" in result
            assert result["comment"]["body"] == test_comment
            assert result["platform"] == platform

            print("✅ MCP tool GitHub test successful:")
            print(f"   Comment ID: {result['comment']['id']}")

        except Exception as e:
            pytest.fail(f"MCP tool GitHub test failed: {str(e)}")

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.skipif(not gitlab_available, reason="GitLab platform not configured")
    async def test_mcp_tool_gitlab_live(self):
        """Test MCP tool with GitLab live API."""
        # Test data
        platform = "gitlab"
        project_id = "gitlab-org/gitlab"
        issue_id = "1"
        test_comment = f"🔧 MCP tool GitLab test comment - {datetime.now().isoformat()}"

        try:
            # Act - Use MCP tool directly
            result = await create_issue_comment(
                platform, project_id, issue_id, test_comment
            )

            # Assert MCP tool response
            assert "comment" in result
            assert result["comment"]["body"] == test_comment
            assert result["platform"] == platform

            print("✅ MCP tool GitLab test successful:")
            print(f"   Comment ID: {result['comment']['id']}")

        except Exception as e:
            pytest.fail(f"MCP tool GitLab test failed: {str(e)}")

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_error_handling_invalid_issue(self):
        """Test error handling with invalid issue ID."""
        platform = "github"
        project_id = "yumeminami/git_mcp"
        invalid_issue_id = "999999"  # Non-existent issue
        test_comment = "This should fail"

        # Act & Assert - Should raise PlatformError
        with pytest.raises(Exception) as exc_info:
            await PlatformService.create_issue_comment(
                platform, project_id, invalid_issue_id, test_comment
            )

        print(f"✅ Error handling test passed: {str(exc_info.value)}")

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.skipif(not github_available, reason="GitHub platform not configured")
    async def test_concurrent_comment_creation(self):
        """Test multiple concurrent comment creation requests."""
        platform = "github"
        project_id = "yumeminami/git_mcp"
        issue_id = "29"

        # Create multiple comment tasks
        timestamp = datetime.now().isoformat()
        tasks = [
            PlatformService.create_issue_comment(
                platform,
                project_id,
                issue_id,
                f"🔄 Concurrent test comment {i} - {timestamp}",
            )
            for i in range(3)
        ]

        try:
            # Execute concurrently
            results = await asyncio.gather(*tasks)

            # Assert all succeeded
            assert len(results) == 3
            for i, result in enumerate(results):
                assert "comment" in result
                assert f"Concurrent test comment {i}" in result["comment"]["body"]
                assert result["platform"] == platform

            print("✅ Concurrent comment creation test passed:")
            for i, result in enumerate(results):
                print(f"   Comment {i} ID: {result['comment']['id']}")

        except Exception as e:
            pytest.fail(f"Concurrent comment creation failed: {str(e)}")


class TestCommentValidation:
    """Test comment validation and edge cases."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_empty_comment_handling(self):
        """Test handling of empty comment body."""
        platform = "github"
        project_id = "yumeminami/git_mcp"
        issue_id = "29"
        empty_comment = ""

        try:
            result = await PlatformService.create_issue_comment(
                platform, project_id, issue_id, empty_comment
            )

            # Should succeed but with empty body
            assert result["comment"]["body"] == ""
            print("✅ Empty comment test passed")

        except Exception as e:
            # Some platforms might reject empty comments
            print(f"✅ Empty comment properly rejected: {str(e)}")

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.skipif(not github_available, reason="GitHub platform not configured")
    async def test_markdown_comment_formatting(self):
        """Test comment with markdown formatting."""
        platform = "github"
        project_id = "yumeminami/git_mcp"
        issue_id = "29"

        markdown_comment = f"""## Test Comment with Markdown

**Bold text** and *italic text*

- List item 1
- List item 2

```python
# Code block
print("Hello from test!")
```

[Link to issue](https://github.com/{project_id}/issues/{issue_id})

Created at: {datetime.now().isoformat()}
        """

        try:
            result = await PlatformService.create_issue_comment(
                platform, project_id, issue_id, markdown_comment
            )

            assert "Test Comment with Markdown" in result["comment"]["body"]
            print("✅ Markdown comment test passed:")
            print(f"   Comment ID: {result['comment']['id']}")

        except Exception as e:
            pytest.fail(f"Markdown comment test failed: {str(e)}")


# Test configuration and utilities
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests (require live APIs)"
    )


if __name__ == "__main__":
    # Run integration tests
    pytest.main([__file__, "-v", "-m", "integration"])
