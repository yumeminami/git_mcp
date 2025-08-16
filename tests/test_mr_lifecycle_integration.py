"""Complete MR lifecycle integration tests: create -> get/list -> close."""

import os
import pytest
from datetime import datetime

from git_mcp.mcp_server import (
    create_merge_request,
    list_merge_requests,
    get_merge_request_details,
    get_merge_request_diff,
    get_merge_request_commits,
    close_merge_request,
)
from git_mcp.core.config import get_config


def check_github_available():
    """Check if GitHub platform is configured and available."""
    try:
        config = get_config()
        platforms = config.list_platforms()
        github_configured = (
            "github" in platforms and config.get_platform("github") is not None
        )
        github_token = os.getenv("GIT_MCP_GITHUB_TOKEN")
        return github_configured or github_token is not None
    except Exception:
        return False


def check_gitlab_available():
    """Check if GitLab platform is configured and available."""
    try:
        config = get_config()
        platforms = config.list_platforms()
        gitlab_configured = (
            "gitlab" in platforms and config.get_platform("gitlab") is not None
        )
        gitlab_token = os.getenv("GIT_MCP_GITLAB_TOKEN")
        return gitlab_configured or gitlab_token is not None
    except Exception:
        return False


def get_github_test_branch():
    """Get GitHub test branch from environment variable."""
    return os.getenv("GIT_MCP_GITHUB_TEST_BRANCH", "test-mr-branch")


def get_gitlab_test_branch():
    """Get GitLab test branch from environment variable."""
    return os.getenv("GIT_MCP_GITLAB_TEST_BRANCH", "test-mr-branch")


github_available = check_github_available()
gitlab_available = check_gitlab_available()


class TestMRLifecycleGitHub:
    """Complete MR lifecycle tests for GitHub: create -> test -> close."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.skipif(not github_available, reason="GitHub platform not configured")
    async def test_github_complete_mr_lifecycle(self):
        """Test complete GitHub PR lifecycle: create -> get/list -> close."""
        platform = "github"
        project_id = "yumeminami/github_test_repo_for_git_mcp"
        source_branch = get_github_test_branch()
        target_branch = "main"

        # Unique identifiers for this test run
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        title = f"🔄 Lifecycle Test PR - {timestamp}"
        description = f"""## MR Lifecycle Integration Test

This PR is created by the automated MR lifecycle test to verify the complete workflow:

**Test Sequence:**
1. ✅ Create PR (this step)
2. 🔄 List PRs (verify creation)
3. 🔄 Get PR details
4. 🔄 Get PR diff
5. 🔄 Get PR commits
6. 🔄 Close PR (cleanup)

**Test Details:**
- Platform: GitHub
- Repository: {project_id}
- Source Branch: {source_branch}
- Target Branch: {target_branch}
- Created: {datetime.now().isoformat()}

This PR will be automatically closed by the test suite.
"""

        created_pr_id = None

        try:
            # Step 1: Create PR
            print("📝 Step 1: Creating GitHub PR...")
            create_result = await create_merge_request(
                platform, project_id, title, source_branch, target_branch, description
            )

            assert "merge_request" in create_result
            assert create_result["platform"] == platform
            created_pr_id = create_result["merge_request"]["id"]

            print(f"✅ Step 1 Complete: PR #{created_pr_id} created successfully")
            print(f"   Title: {create_result['merge_request']['title']}")
            print(f"   URL: {create_result['merge_request'].get('url', 'N/A')}")

            # Step 2: List PRs (verify creation)
            print("📋 Step 2: Listing PRs to verify creation...")
            list_result = await list_merge_requests(
                platform, project_id, state="all", limit=10
            )

            assert isinstance(list_result, list)
            # Find our created PR in the list
            our_pr = next((pr for pr in list_result if pr["id"] == created_pr_id), None)
            assert our_pr is not None, f"Created PR #{created_pr_id} not found in list"
            assert our_pr["title"] == title

            print("✅ Step 2 Complete: PR found in list with correct title")

            # Step 3: Get PR details
            print("🔍 Step 3: Getting PR details...")
            details_result = await get_merge_request_details(
                platform, project_id, created_pr_id
            )

            assert details_result["id"] == created_pr_id
            assert details_result["title"] == title
            assert "state" in details_result
            assert "author" in details_result

            print("✅ Step 3 Complete: PR details retrieved")
            print(f"   State: {details_result['state']}")
            print(f"   Author: {details_result['author']}")

            # Step 4: Get PR diff
            print("📊 Step 4: Getting PR diff...")
            diff_result = await get_merge_request_diff(
                platform, project_id, created_pr_id
            )

            assert "mr_id" in diff_result
            assert diff_result["mr_id"] == created_pr_id
            # Note: diff may be empty if no file changes, that's okay

            print("✅ Step 4 Complete: PR diff retrieved")

            # Step 5: Get PR commits
            print("📝 Step 5: Getting PR commits...")
            commits_result = await get_merge_request_commits(
                platform, project_id, created_pr_id
            )

            assert "mr_id" in commits_result
            assert commits_result["mr_id"] == created_pr_id
            # Note: commits may be empty for some PRs, that's okay

            print("✅ Step 5 Complete: PR commits retrieved")

            # Step 6: Close PR
            print("🔒 Step 6: Closing PR...")
            close_result = await close_merge_request(
                platform, project_id, created_pr_id
            )

            assert "merge_request" in close_result
            assert close_result["platform"] == platform
            assert close_result["mr_id"] == created_pr_id
            assert "closed" in close_result["message"].lower()

            # Verify the PR is actually closed
            closed_details = await get_merge_request_details(
                platform, project_id, created_pr_id
            )
            assert closed_details["state"] == "closed"

            print("✅ Step 6 Complete: PR successfully closed")
            print(f"   Final State: {closed_details['state']}")

            print("\n🎉 GitHub MR Lifecycle Test PASSED!")
            print("   All 6 steps completed successfully")
            print(f"   PR #{created_pr_id} created and closed cleanly")

        except Exception as e:
            if created_pr_id:
                print(f"🚨 Test failed, attempting cleanup of PR #{created_pr_id}")
                try:
                    await close_merge_request(platform, project_id, created_pr_id)
                    print(f"🧹 Cleanup successful: PR #{created_pr_id} closed")
                except Exception as cleanup_error:
                    print(f"⚠️ Cleanup failed: {cleanup_error}")

            pytest.fail(f"GitHub MR lifecycle test failed: {str(e)}")


class TestMRLifecycleGitLab:
    """Complete MR lifecycle tests for GitLab: create -> test -> close."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.skipif(not gitlab_available, reason="GitLab platform not configured")
    async def test_gitlab_complete_mr_lifecycle(self):
        """Test complete GitLab MR lifecycle: create -> get/list -> close."""
        platform = "gitlab"
        project_id = "fengrongman-group/gitlab_test_repo_for_git_mcp"
        source_branch = get_gitlab_test_branch()
        target_branch = "main"

        # Unique identifiers for this test run
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        title = f"🔄 Lifecycle Test MR - {timestamp}"
        description = f"""## MR Lifecycle Integration Test

This MR is created by the automated MR lifecycle test to verify the complete workflow:

**Test Sequence:**
1. ✅ Create MR (this step)
2. 🔄 List MRs (verify creation)
3. 🔄 Get MR details
4. 🔄 Get MR diff
5. 🔄 Get MR commits
6. 🔄 Close MR (cleanup)

**Test Details:**
- Platform: GitLab
- Project: {project_id}
- Source Branch: {source_branch}
- Target Branch: {target_branch}
- Created: {datetime.now().isoformat()}

This MR will be automatically closed by the test suite.
"""

        created_mr_id = None

        try:
            # Step 1: Create MR
            print("📝 Step 1: Creating GitLab MR...")
            create_result = await create_merge_request(
                platform, project_id, title, source_branch, target_branch, description
            )

            assert "merge_request" in create_result
            assert create_result["platform"] == platform
            created_mr_id = create_result["merge_request"]["id"]

            print(f"✅ Step 1 Complete: MR !{created_mr_id} created successfully")
            print(f"   Title: {create_result['merge_request']['title']}")
            print(f"   URL: {create_result['merge_request'].get('url', 'N/A')}")

            # Step 2: List MRs (verify creation)
            print("📋 Step 2: Listing MRs to verify creation...")
            list_result = await list_merge_requests(
                platform, project_id, state="all", limit=10
            )

            assert isinstance(list_result, list)
            # Find our created MR in the list
            our_mr = next((mr for mr in list_result if mr["id"] == created_mr_id), None)
            assert our_mr is not None, f"Created MR !{created_mr_id} not found in list"
            assert our_mr["title"] == title

            print("✅ Step 2 Complete: MR found in list with correct title")

            # Step 3: Get MR details
            print("🔍 Step 3: Getting MR details...")
            details_result = await get_merge_request_details(
                platform, project_id, created_mr_id
            )

            assert details_result["id"] == created_mr_id
            assert details_result["title"] == title
            assert "state" in details_result
            assert "author" in details_result

            print("✅ Step 3 Complete: MR details retrieved")
            print(f"   State: {details_result['state']}")
            print(f"   Author: {details_result['author']}")

            # Step 4: Get MR diff
            print("📊 Step 4: Getting MR diff...")
            diff_result = await get_merge_request_diff(
                platform, project_id, created_mr_id
            )

            assert "mr_id" in diff_result
            assert diff_result["mr_id"] == created_mr_id

            print("✅ Step 4 Complete: MR diff retrieved")

            # Step 5: Get MR commits
            print("📝 Step 5: Getting MR commits...")
            commits_result = await get_merge_request_commits(
                platform, project_id, created_mr_id
            )

            assert "mr_id" in commits_result
            assert commits_result["mr_id"] == created_mr_id

            print("✅ Step 5 Complete: MR commits retrieved")

            # Step 6: Close MR
            print("🔒 Step 6: Closing MR...")
            close_result = await close_merge_request(
                platform, project_id, created_mr_id
            )

            assert "merge_request" in close_result
            assert close_result["platform"] == platform
            assert close_result["mr_id"] == created_mr_id
            assert "closed" in close_result["message"].lower()

            # Verify the MR is actually closed
            closed_details = await get_merge_request_details(
                platform, project_id, created_mr_id
            )
            assert closed_details["state"] == "closed"

            print("✅ Step 6 Complete: MR successfully closed")
            print(f"   Final State: {closed_details['state']}")

            print("\n🎉 GitLab MR Lifecycle Test PASSED!")
            print("   All 6 steps completed successfully")
            print(f"   MR !{created_mr_id} created and closed cleanly")

        except Exception as e:
            if created_mr_id:
                print(f"🚨 Test failed, attempting cleanup of MR !{created_mr_id}")
                try:
                    await close_merge_request(platform, project_id, created_mr_id)
                    print(f"🧹 Cleanup successful: MR !{created_mr_id} closed")
                except Exception as cleanup_error:
                    print(f"⚠️ Cleanup failed: {cleanup_error}")

            pytest.fail(f"GitLab MR lifecycle test failed: {str(e)}")


class TestMRCrossValidation:
    """Cross-platform validation tests."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.skipif(
        not (github_available and gitlab_available),
        reason="Both GitHub and GitLab platforms required",
    )
    async def test_cross_platform_mr_workflow_consistency(self):
        """Test that MR workflows behave consistently across platforms."""
        # This test validates that both platforms support the same workflow
        # without actually creating MRs (just testing API availability)

        github_project = "yumeminami/github_test_repo_for_git_mcp"
        gitlab_project = "fengrongman-group/gitlab_test_repo_for_git_mcp"

        try:
            # Test that both platforms can list MRs
            github_mrs = await list_merge_requests(
                "github", github_project, state="all", limit=1
            )
            gitlab_mrs = await list_merge_requests(
                "gitlab", gitlab_project, state="all", limit=1
            )

            assert isinstance(github_mrs, list)
            assert isinstance(gitlab_mrs, list)

            # Test consistent response structure if MRs exist
            if github_mrs and gitlab_mrs:
                github_mr = github_mrs[0]
                gitlab_mr = gitlab_mrs[0]

                # Both should have the same basic fields
                common_fields = ["id", "title", "state", "url", "author", "platform"]
                for field in common_fields:
                    assert field in github_mr, f"GitHub MR missing field: {field}"
                    assert field in gitlab_mr, f"GitLab MR missing field: {field}"

                # Platform identification should be correct
                assert github_mr["platform"] == "github"
                assert gitlab_mr["platform"] == "gitlab"

            print("✅ Cross-platform MR workflow consistency validated")

        except Exception as e:
            pytest.fail(f"Cross-platform consistency test failed: {str(e)}")


# Test configuration and utilities
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests (require live APIs)"
    )


if __name__ == "__main__":
    # Run lifecycle integration tests
    pytest.main([__file__, "-v", "-m", "integration"])
