"""Platform service - shared business logic for CLI and MCP."""

import os
import re
from typing import List, Dict, Any, Optional, Tuple
from urllib.parse import urlparse

from ..core.config import get_config


class PlatformService:
    """Shared service for platform operations."""

    @staticmethod
    def get_adapter(platform_name: str):
        """Get platform adapter based on configuration or environment variables."""
        config = get_config()
        platform_config = config.get_platform(platform_name)

        # If no platform config found, try to create from environment variables
        if not platform_config:
            # Try environment variable fallback for CI/testing
            if platform_name == "github":
                github_token = os.getenv("GIT_MCP_GITHUB_TOKEN")
                if github_token:
                    from ..platforms.github import GitHubAdapter

                    try:
                        # Create adapter with temporary username, then get real username
                        github_adapter = GitHubAdapter(
                            "https://github.com", github_token, "temp"
                        )
                        # Try to get username from API
                        user_info = (
                            github_adapter.client.get_user()
                            if github_adapter.client
                            else None
                        )
                        username = user_info.login if user_info else "ci-user"
                        # Create new adapter with correct username
                        return GitHubAdapter(
                            "https://github.com", github_token, username
                        )
                    except Exception:
                        # Fallback to default username if API call fails
                        return GitHubAdapter(
                            "https://github.com", github_token, "ci-user"
                        )
            elif platform_name == "gitlab":
                gitlab_token = os.getenv("GIT_MCP_GITLAB_TOKEN")
                if gitlab_token:
                    from ..platforms.gitlab import GitLabAdapter

                    try:
                        # Create adapter with temporary username, then get real username
                        gitlab_adapter = GitLabAdapter(
                            "https://gitlab.com", gitlab_token, "temp"
                        )
                        # Try to authenticate and get username from API
                        try:
                            user_info = gitlab_adapter.client.user  # type: ignore
                            username = getattr(user_info, "username", "ci-user")
                        except Exception:
                            username = "ci-user"
                        # Create new adapter with correct username
                        return GitLabAdapter(
                            "https://gitlab.com", gitlab_token, username
                        )
                    except Exception:
                        # Fallback to default username if API call fails
                        return GitLabAdapter(
                            "https://gitlab.com", gitlab_token, "ci-user"
                        )

            raise ValueError(f"Platform '{platform_name}' not found")

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
            raise ValueError(
                f"Platform type '{platform_config.type}' not supported yet"
            )

    @staticmethod
    def parse_issue_url(url: str) -> Tuple[str, str, str]:
        """
        Parse an issue URL to extract platform info, project ID, and issue ID.

        Supports formats like:
        - https://gitlab.com/group/project/-/issues/123
        - https://gitlab.example.com/group/subgroup/project/-/issues/456
        - https://github.com/user/repo/issues/789

        Returns:
            Tuple[platform_name, project_id, issue_id]
        """
        parsed = urlparse(url)
        host = parsed.netloc
        path = parsed.path

        # Find configured platform by URL
        config = get_config()
        platform_name = None

        for name in config.list_platforms():
            platform_config = config.get_platform(name)
            if platform_config and host in platform_config.url:
                platform_name = name
                break

        if not platform_name:
            raise ValueError(f"No configured platform found for host: {host}")

        platform_config = config.get_platform(platform_name)

        if platform_config.type == "gitlab":
            # GitLab URL format: /group/project/-/issues/123
            match = re.search(r"/([^/]+(?:/[^/]+)*?)/-/issues/(\d+)", path)
            if match:
                project_path, issue_id = match.groups()
                return platform_name, project_path, issue_id
        elif platform_config.type == "github":
            # GitHub URL format: /user/repo/issues/123
            match = re.search(r"/([^/]+/[^/]+)/issues/(\d+)", path)
            if match:
                project_path, issue_id = match.groups()
                return platform_name, project_path, issue_id

        raise ValueError(f"Could not parse issue URL: {url}")

    @staticmethod
    def parse_project_url(url: str) -> Tuple[str, str]:
        """
        Parse a project URL to extract platform info and project ID.

        Returns:
            Tuple[platform_name, project_id]
        """
        parsed = urlparse(url)
        host = parsed.netloc
        path = parsed.path.strip("/")

        # Find configured platform by URL
        config = get_config()
        platform_name = None

        for name in config.list_platforms():
            platform_config = config.get_platform(name)
            if platform_config and host in platform_config.url:
                platform_name = name
                break

        if not platform_name:
            raise ValueError(f"No configured platform found for host: {host}")

        # For most Git platforms, the path is the project ID
        project_id = path
        return platform_name, project_id

    @staticmethod
    async def list_platforms() -> List[Dict[str, str]]:
        """List all configured platforms."""
        config = get_config()
        platforms = config.list_platforms()

        result = []
        for platform_name in platforms:
            platform_config = config.get_platform(platform_name)
            result.append(
                {
                    "name": platform_name,
                    "type": platform_config.type,
                    "url": platform_config.url,
                    "username": platform_config.username or "",
                }
            )
        return result

    @staticmethod
    async def list_my_issues(
        platform_name: str,
        project_id: str,
        state: str = "opened",
        limit: Optional[int] = 20,
        **filters,
    ) -> List[Dict[str, Any]]:
        """List issues assigned to the current user."""
        try:
            config = get_config()
            platform_config = config.get_platform(platform_name)

            username = None
            if platform_config and platform_config.username:
                username = platform_config.username
            else:
                # Try to get username from adapter (works with env vars)
                try:
                    adapter = PlatformService.get_adapter(platform_name)
                    user_info = await adapter.get_current_user()
                    username = user_info.get("username") or user_info.get("login")
                except Exception:  # nosec B110
                    # Failed to fetch username from API, will use fallback
                    pass

            if not username:
                raise ValueError(
                    f"No username configured for platform '{platform_name}'. "
                    f"Use 'refresh_platform_username' to fetch it automatically."
                )

            # Add assignee filter for current user
            filters["assignee"] = username

            return await PlatformService.list_issues(
                platform_name, project_id, state, limit, **filters
            )
        except Exception as e:
            raise Exception(f"Failed to list my issues: {str(e)}")

    @staticmethod
    async def list_my_merge_requests(
        platform_name: str,
        project_id: str,
        state: str = "opened",
        limit: Optional[int] = 20,
        **filters,
    ) -> List[Dict[str, Any]]:
        """List merge requests created by the current user."""
        try:
            config = get_config()
            platform_config = config.get_platform(platform_name)

            username = None
            if platform_config and platform_config.username:
                username = platform_config.username
            else:
                # Try to get username from adapter (works with env vars)
                try:
                    adapter = PlatformService.get_adapter(platform_name)
                    user_info = await adapter.get_current_user()
                    username = user_info.get("username") or user_info.get("login")
                except Exception:  # nosec B110
                    # Failed to fetch username from API, will use fallback
                    pass

            if not username:
                raise ValueError(
                    f"No username configured for platform '{platform_name}'. "
                    f"Use 'refresh_platform_username' to fetch it automatically."
                )

            # Add author filter for current user
            filters["author"] = username

            return await PlatformService.list_merge_requests(
                platform_name, project_id, state, limit, **filters
            )
        except Exception as e:
            raise Exception(f"Failed to list my merge requests: {str(e)}")

    @staticmethod
    async def get_platform_config(platform_name: str) -> Dict[str, Any]:
        """Get configuration for a specific platform."""
        try:
            config = get_config()
            platform_config = config.get_platform(platform_name)

            if not platform_config:
                return {
                    "platform": platform_name,
                    "found": False,
                    "message": f"Platform '{platform_name}' not found",
                }

            return {
                "platform": platform_name,
                "found": True,
                "type": platform_config.type,
                "url": platform_config.url,
                "username": platform_config.username,
                "has_token": bool(platform_config.token),
                "message": f"Configuration for '{platform_name}'",
            }
        except Exception as e:
            return {
                "platform": platform_name,
                "found": False,
                "message": f"Error getting platform config: {str(e)}",
            }

    @staticmethod
    async def get_current_user_info(platform_name: str) -> Dict[str, Any]:
        """Get current user information from platform API."""
        try:
            adapter = PlatformService.get_adapter(platform_name)
            user_info = await adapter.get_current_user()

            return {
                "platform": platform_name,
                "success": True,
                "user_info": user_info,
                "username": user_info.get("username", "Unknown"),
                "message": f"User info retrieved from '{platform_name}'",
            }
        except Exception as e:
            return {
                "platform": platform_name,
                "success": False,
                "user_info": None,
                "username": None,
                "message": f"Failed to get user info: {str(e)}",
            }

    @staticmethod
    async def refresh_platform_username(platform_name: str) -> Dict[str, Any]:
        """Refresh username for a platform configuration."""
        try:
            config = get_config()
            success = await config.refresh_username(platform_name)
            platform_config = config.get_platform(platform_name)

            return {
                "platform": platform_name,
                "success": success,
                "username": platform_config.username if platform_config else None,
                "message": f"Username refreshed for '{platform_name}'"
                if success
                else f"Could not refresh username for '{platform_name}'",
            }
        except Exception as e:
            return {
                "platform": platform_name,
                "success": False,
                "username": None,
                "message": f"Failed to refresh username: {str(e)}",
            }

    @staticmethod
    async def test_platform_connection(platform_name: str) -> Dict[str, Any]:
        """Test connection to a platform."""
        try:
            adapter = PlatformService.get_adapter(platform_name)
            success = await adapter.test_connection()

            return {
                "platform": platform_name,
                "success": success,
                "message": f"Connection to '{platform_name}' successful"
                if success
                else f"Connection to '{platform_name}' failed",
            }
        except Exception as e:
            return {
                "platform": platform_name,
                "success": False,
                "message": f"Connection test failed: {str(e)}",
            }

    @staticmethod
    async def list_projects(
        platform_name: str, limit: Optional[int] = 20, **filters
    ) -> List[Dict[str, Any]]:
        """List projects from a platform."""
        adapter = PlatformService.get_adapter(platform_name)

        # Prepare filters
        if limit:
            filters["per_page"] = limit

        projects = await adapter.list_projects(**filters)

        return [
            {
                "id": project.id,
                "name": project.title,
                "description": project.metadata.get("description", "")
                if project.metadata
                else "",
                "url": project.url,
                "visibility": project.metadata.get("visibility", "")
                if project.metadata
                else "",
                "created_at": project.created_at.isoformat()
                if project.created_at
                else None,
                "updated_at": project.updated_at.isoformat()
                if project.updated_at
                else None,
                "platform": platform_name,
            }
            for project in projects
        ]

    @staticmethod
    async def get_project_details(
        platform_name: str, project_id: str
    ) -> Dict[str, Any]:
        """Get detailed project information."""
        adapter = PlatformService.get_adapter(platform_name)
        project = await adapter.get_project(project_id)

        if not project:
            raise ValueError(f"Project '{project_id}' not found")

        return {
            "id": project.id,
            "name": project.title,
            "description": project.metadata.get("description", "")
            if project.metadata
            else "",
            "url": project.url,
            "visibility": project.metadata.get("visibility", "")
            if project.metadata
            else "",
            "default_branch": project.metadata.get("default_branch", "")
            if project.metadata
            else "",
            "created_at": project.created_at.isoformat()
            if project.created_at
            else None,
            "updated_at": project.updated_at.isoformat()
            if project.updated_at
            else None,
            "author": project.author,
            "platform": platform_name,
            "full_info": project.metadata or {},
        }

    @staticmethod
    async def create_project(platform_name: str, name: str, **kwargs) -> Dict[str, Any]:
        """Create a new project."""
        adapter = PlatformService.get_adapter(platform_name)
        project = await adapter.create_project(name, **kwargs)

        return {
            "id": project.id,
            "name": project.title,
            "description": project.metadata.get("description", "")
            if project.metadata
            else "",
            "url": project.url,
            "platform": platform_name,
            "message": f"Project '{name}' created successfully",
        }

    @staticmethod
    async def delete_project(platform_name: str, project_id: str) -> Dict[str, Any]:
        """Delete a project."""
        adapter = PlatformService.get_adapter(platform_name)
        success = await adapter.delete_project(project_id)

        return {
            "project_id": project_id,
            "platform": platform_name,
            "success": success,
            "message": f"Project '{project_id}' deleted successfully"
            if success
            else f"Failed to delete project '{project_id}'",
        }

    @staticmethod
    async def list_issues(
        platform_name: str,
        project_id: str,
        state: str = "opened",
        limit: Optional[int] = 20,
        **filters,
    ) -> List[Dict[str, Any]]:
        """List issues in a project."""
        adapter = PlatformService.get_adapter(platform_name)

        # Prepare filters
        filters["state"] = state
        if limit:
            filters["per_page"] = limit

        issues = await adapter.list_issues(project_id, **filters)

        return [
            {
                "id": issue.id,
                "title": issue.title,
                "description": issue.description or "",
                "state": issue.state.value if issue.state else "unknown",
                "url": issue.url,
                "author": issue.author,
                "assignee": issue.assignee,
                "created_at": issue.created_at.isoformat()
                if issue.created_at
                else None,
                "updated_at": issue.updated_at.isoformat()
                if issue.updated_at
                else None,
                "labels": issue.metadata.get("labels", []) if issue.metadata else [],
                "platform": platform_name,
                "project_id": project_id,
            }
            for issue in issues
        ]

    @staticmethod
    async def list_all_issues(
        platform_name: str,
        state: str = "opened",
        limit: Optional[int] = 20,
        **filters,
    ) -> List[Dict[str, Any]]:
        """List issues across all projects (global search)."""
        adapter = PlatformService.get_adapter(platform_name)
        # Prepare filters
        filters["state"] = state
        if limit:
            filters["per_page"] = limit

        issues = await adapter.list_all_issues(**filters)
        return [
            {
                "id": issue.id,
                "title": issue.title,
                "description": issue.description or "",
                "state": issue.state.value if issue.state else "unknown",
                "url": issue.url,
                "author": issue.author,
                "assignee": issue.assignee,
                "created_at": issue.created_at.isoformat()
                if issue.created_at
                else None,
                "updated_at": issue.updated_at.isoformat()
                if issue.updated_at
                else None,
                "labels": issue.metadata.get("labels", []) if issue.metadata else [],
                "platform": platform_name,
                "project_id": issue.project_id,
            }
            for issue in issues
        ]

    @staticmethod
    async def get_issue_details(
        platform_name: str, project_id: str, issue_id: str
    ) -> Dict[str, Any]:
        """Get detailed issue information including comments."""
        adapter = PlatformService.get_adapter(platform_name)
        issue = await adapter.get_issue(project_id, issue_id)

        if not issue:
            raise ValueError(f"Issue '{issue_id}' not found in project '{project_id}'")

        result = {
            "id": issue.id,
            "title": issue.title,
            "description": issue.description or "",
            "state": issue.state.value if issue.state else "unknown",
            "url": issue.url,
            "author": issue.author,
            "assignee": issue.assignee,
            "created_at": issue.created_at.isoformat() if issue.created_at else None,
            "updated_at": issue.updated_at.isoformat() if issue.updated_at else None,
            "labels": issue.metadata.get("labels", []) if issue.metadata else [],
            "platform": platform_name,
            "project_id": project_id,
            "comments": [],
        }

        # Add comments if available
        if issue.metadata and "comments" in issue.metadata:
            result["comments"] = issue.metadata["comments"]

        return result

    @staticmethod
    async def get_issue_by_url(url: str) -> Dict[str, Any]:
        """Get issue details by URL."""
        platform_name, project_id, issue_id = PlatformService.parse_issue_url(url)
        return await PlatformService.get_issue_details(
            platform_name, project_id, issue_id
        )

    @staticmethod
    async def create_issue(
        platform_name: str,
        project_id: str,
        title: str,
        description: Optional[str] = None,
        labels: Optional[List[str]] = None,
        assignee: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Create a new issue."""
        adapter = PlatformService.get_adapter(platform_name)

        # Prepare kwargs
        if description:
            kwargs["description"] = description
        if labels:
            kwargs["labels"] = ",".join(labels)
        if assignee:
            kwargs["assignee_username"] = assignee

        issue = await adapter.create_issue(project_id, title, **kwargs)

        return {
            "id": issue.id,
            "title": issue.title,
            "description": issue.description or "",
            "state": issue.state.value if issue.state else "unknown",
            "url": issue.url,
            "author": issue.author,
            "assignee": issue.assignee,
            "created_at": issue.created_at.isoformat() if issue.created_at else None,
            "platform": platform_name,
            "project_id": project_id,
            "message": f"Issue '{title}' created successfully",
        }

    @staticmethod
    async def update_issue(
        platform_name: str, project_id: str, issue_id: str, **kwargs
    ) -> Dict[str, Any]:
        """Update an issue."""
        adapter = PlatformService.get_adapter(platform_name)
        issue = await adapter.update_issue(project_id, issue_id, **kwargs)

        return {
            "id": issue.id,
            "title": issue.title,
            "state": issue.state.value if issue.state else "unknown",
            "url": issue.url,
            "platform": platform_name,
            "project_id": project_id,
            "message": f"Issue '{issue_id}' updated successfully",
        }

    @staticmethod
    async def close_issue(
        platform_name: str, project_id: str, issue_id: str
    ) -> Dict[str, Any]:
        """Close an issue."""
        adapter = PlatformService.get_adapter(platform_name)
        issue = await adapter.close_issue(project_id, issue_id)

        return {
            "id": issue.id,
            "title": issue.title,
            "state": issue.state.value if issue.state else "unknown",
            "url": issue.url,
            "platform": platform_name,
            "project_id": project_id,
            "message": f"Issue '{issue_id}' closed successfully",
        }

    @staticmethod
    async def create_issue_comment(
        platform_name: str, project_id: str, issue_id: str, body: str, **kwargs
    ) -> Dict[str, Any]:
        """Create a comment on an issue."""
        adapter = PlatformService.get_adapter(platform_name)
        comment_data = await adapter.create_issue_comment(
            project_id, issue_id, body, **kwargs
        )

        return {
            "comment": comment_data,
            "issue_id": issue_id,
            "project_id": project_id,
            "platform": platform_name,
            "message": f"Comment created successfully on issue {issue_id}",
        }

    @staticmethod
    async def list_merge_requests(
        platform_name: str,
        project_id: str,
        state: str = "opened",
        limit: Optional[int] = 20,
        **filters,
    ) -> List[Dict[str, Any]]:
        """List merge requests in a project."""
        adapter = PlatformService.get_adapter(platform_name)

        # Prepare filters
        filters["state"] = state
        if limit:
            filters["per_page"] = limit

        mrs = await adapter.list_merge_requests(project_id, **filters)

        return [
            {
                "id": mr.id,
                "title": mr.title,
                "description": mr.description or "",
                "state": mr.state.value if mr.state else "unknown",
                "url": mr.url,
                "author": mr.author,
                "assignee": mr.assignee,
                "source_branch": mr.metadata.get("source_branch", "")
                if mr.metadata
                else "",
                "target_branch": mr.metadata.get("target_branch", "")
                if mr.metadata
                else "",
                "created_at": mr.created_at.isoformat() if mr.created_at else None,
                "updated_at": mr.updated_at.isoformat() if mr.updated_at else None,
                "platform": platform_name,
                "project_id": project_id,
            }
            for mr in mrs
        ]

    @staticmethod
    async def get_merge_request_details(
        platform_name: str, project_id: str, mr_id: str
    ) -> Dict[str, Any]:
        """Get detailed merge request information."""
        adapter = PlatformService.get_adapter(platform_name)
        mr = await adapter.get_merge_request(project_id, mr_id)

        if not mr:
            raise ValueError(
                f"Merge request '{mr_id}' not found in project '{project_id}'"
            )

        return {
            "id": mr.id,
            "title": mr.title,
            "description": mr.description or "",
            "state": mr.state.value if mr.state else "unknown",
            "url": mr.url,
            "author": mr.author,
            "assignee": mr.assignee,
            "source_branch": mr.metadata.get("source_branch", "")
            if mr.metadata
            else "",
            "target_branch": mr.metadata.get("target_branch", "")
            if mr.metadata
            else "",
            "created_at": mr.created_at.isoformat() if mr.created_at else None,
            "updated_at": mr.updated_at.isoformat() if mr.updated_at else None,
            "platform": platform_name,
            "project_id": project_id,
            "full_info": mr.metadata or {},
        }

    @staticmethod
    async def create_merge_request(
        platform_name: str,
        project_id: str,
        title: str,
        source_branch: str,
        target_branch: str = "main",
        **kwargs,
    ) -> Dict[str, Any]:
        """Create a new merge request."""
        adapter = PlatformService.get_adapter(platform_name)
        mr = await adapter.create_merge_request(
            project_id, source_branch, target_branch, title, **kwargs
        )

        return {
            "merge_request": {
                "id": mr.id,
                "title": mr.title,
                "url": mr.url,
                "source_branch": source_branch,
                "target_branch": target_branch,
            },
            "platform": platform_name,
            "project_id": project_id,
            "message": f"Merge request '{title}' created successfully",
        }

    # Fork operations
    @staticmethod
    async def create_fork(
        platform_name: str, project_id: str, **kwargs
    ) -> Dict[str, Any]:
        """Create a fork of a repository."""
        adapter = PlatformService.get_adapter(platform_name)
        fork = await adapter.create_fork(project_id, **kwargs)

        return {
            "id": fork.id,
            "title": fork.title,
            "url": fork.url,
            "namespace": fork.namespace,
            "visibility": fork.visibility,
            "clone_url_http": fork.clone_url_http,
            "clone_url_ssh": fork.clone_url_ssh,
            "platform": platform_name,
            "original_project_id": project_id,
            "message": f"Fork of '{project_id}' created successfully as '{fork.id}'",
            "full_info": fork.metadata or {},
        }

    @staticmethod
    async def get_fork_info(platform_name: str, project_id: str) -> Dict[str, Any]:
        """Get fork information for a repository."""
        adapter = PlatformService.get_adapter(platform_name)

        is_fork = await adapter.is_fork(project_id)
        parent_id = None

        if is_fork:
            parent_id = await adapter.get_fork_parent(project_id)

        return {
            "project_id": project_id,
            "is_fork": is_fork,
            "parent_id": parent_id,
            "platform": platform_name,
        }

    @staticmethod
    async def list_forks(
        platform_name: str, project_id: str, limit: Optional[int] = 20
    ) -> List[Dict[str, Any]]:
        """List forks of a repository."""
        # Note: This is a basic implementation
        # Full implementation would require additional API calls to list forks
        # For now, we'll return a message indicating this functionality
        return [
            {
                "project_id": project_id,
                "platform": platform_name,
                "limit": limit,
                "message": "Fork listing functionality requires additional implementation",
                "note": "Use GitHub/GitLab web interface to view forks for now",
            }
        ]

    @staticmethod
    async def get_merge_request_diff(
        platform_name: str, project_id: str, mr_id: str, **options
    ) -> Dict[str, Any]:
        """Get diff/changes for a merge request."""
        adapter = PlatformService.get_adapter(platform_name)
        diff_data = await adapter.get_merge_request_diff(project_id, mr_id, **options)

        diff_data.update(
            {"platform": platform_name, "project_id": project_id, "mr_id": mr_id}
        )

        return diff_data

    @staticmethod
    async def get_merge_request_commits(
        platform_name: str, project_id: str, mr_id: str, **filters
    ) -> Dict[str, Any]:
        """Get commits for a merge request."""
        adapter = PlatformService.get_adapter(platform_name)
        commits_data = await adapter.get_merge_request_commits(
            project_id, mr_id, **filters
        )

        commits_data.update(
            {"platform": platform_name, "project_id": project_id, "mr_id": mr_id}
        )

        return commits_data

    @staticmethod
    async def close_merge_request(
        platform_name: str, project_id: str, mr_id: str, **kwargs
    ) -> Dict[str, Any]:
        """Close a merge request without merging."""
        adapter = PlatformService.get_adapter(platform_name)
        mr_resource = await adapter.close_merge_request(project_id, mr_id, **kwargs)

        return {
            "merge_request": mr_resource,
            "message": f"Merge request {mr_id} closed successfully",
            "platform": platform_name,
            "project_id": project_id,
            "mr_id": mr_id,
        }

    @staticmethod
    async def update_merge_request(
        platform_name: str, project_id: str, mr_id: str, **kwargs
    ) -> Dict[str, Any]:
        """Update a merge request (title, description, etc.)."""
        adapter = PlatformService.get_adapter(platform_name)
        mr_resource = await adapter.update_merge_request(project_id, mr_id, **kwargs)

        return {
            "merge_request": mr_resource,
            "message": f"Merge request {mr_id} updated successfully",
            "platform": platform_name,
            "project_id": project_id,
            "mr_id": mr_id,
        }
