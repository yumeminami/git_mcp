"""GitHub platform adapter for git-mcp."""

from github import Github, GithubException, BadCredentialsException
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


class GitHubAdapter(PlatformAdapter):
    """GitHub platform adapter using PyGithub."""

    def __init__(
        self,
        url: str = "https://github.com",
        token: Optional[str] = None,
        username: Optional[str] = None,
    ):
        # For GitHub Enterprise, extract base URL
        if url and url != "https://github.com":
            # GitHub Enterprise format: https://github.enterprise.com/api/v3
            if not url.endswith("/api/v3"):
                url = url.rstrip("/") + "/api/v3"
        else:
            url = "https://api.github.com"

        super().__init__(url, token, username)
        self.client: Optional[Github] = None
        self._base_url = url

    @property
    def platform_name(self) -> str:
        return "github"

    async def authenticate(self) -> bool:
        """Authenticate with GitHub."""
        if not self.token:
            raise AuthenticationError("GitHub token is required")

        try:
            if self._base_url == "https://api.github.com":
                self.client = Github(self.token)
            else:
                # GitHub Enterprise
                self.client = Github(base_url=self._base_url, login_or_token=self.token)

            # Test authentication by getting current user
            self.client.get_user()
            self._authenticated = True
            return True
        except BadCredentialsException as e:
            raise AuthenticationError(f"GitHub authentication failed: {e}")
        except Exception as e:
            raise NetworkError(f"Failed to connect to GitHub: {e}")

    async def test_connection(self) -> bool:
        """Test connection to GitHub."""
        if not self.client:
            await self.authenticate()

        try:
            self.client.get_user()
            return True
        except Exception:
            return False

    # Project operations
    async def list_projects(self, **filters) -> List[ProjectResource]:
        """List GitHub repositories."""
        if not self.client:
            await self.authenticate()

        try:
            repos = []
            user = self.client.get_user()

            # Determine what repos to fetch based on filters
            if filters.get("owned", False):
                repos = user.get_repos(type="owner")
            elif filters.get("starred", False):
                repos = user.get_starred()
            else:
                # Default: all accessible repos
                repos = user.get_repos()

            # Apply additional filters
            result_repos = []
            for repo in repos:
                if filters.get("archived") is not None:
                    if repo.archived != filters["archived"]:
                        continue

                if filters.get("search"):
                    search_term = filters["search"].lower()
                    if (
                        search_term not in repo.name.lower()
                        and search_term not in (repo.description or "").lower()
                    ):
                        continue

                result_repos.append(self._convert_to_project_resource(repo))

            return result_repos
        except GithubException as e:
            raise PlatformError(f"Failed to list repositories: {e}", self.platform_name)

    async def get_project(self, project_id: str) -> Optional[ProjectResource]:
        """Get a specific GitHub repository."""
        if not self.client:
            await self.authenticate()

        try:
            repo = self.client.get_repo(project_id)
            return self._convert_to_project_resource(repo)
        except GithubException as e:
            if e.status == 404:
                return None
            raise PlatformError(
                f"Failed to get repository {project_id}: {e}", self.platform_name
            )

    async def create_project(self, name: str, **kwargs) -> ProjectResource:
        """Create a new GitHub repository."""
        if not self.client:
            await self.authenticate()

        try:
            user = self.client.get_user()
            repo_kwargs = {
                "name": name,
                "description": kwargs.get("description", ""),
                "private": kwargs.get("visibility", "private") == "private",
                "auto_init": kwargs.get("initialize_with_readme", False),
                **{
                    k: v
                    for k, v in kwargs.items()
                    if k in ["homepage", "has_issues", "has_wiki", "has_downloads"]
                },
            }
            repo = user.create_repo(**repo_kwargs)
            return self._convert_to_project_resource(repo)
        except GithubException as e:
            raise PlatformError(f"Failed to create repository: {e}", self.platform_name)

    async def delete_project(self, project_id: str) -> bool:
        """Delete a GitHub repository."""
        if not self.client:
            await self.authenticate()

        try:
            repo = self.client.get_repo(project_id)
            repo.delete()
            return True
        except GithubException as e:
            if e.status == 404:
                raise ResourceNotFoundError(
                    "repository", project_id, self.platform_name
                )
            raise PlatformError(
                f"Failed to delete repository {project_id}: {e}", self.platform_name
            )

    # Issue operations
    async def list_issues(self, project_id: str, **filters) -> List[IssueResource]:
        """List issues for a GitHub repository."""
        if not self.client:
            await self.authenticate()

        try:
            repo = self.client.get_repo(project_id)
            github_filters = self._normalize_issue_filters(filters)
            issues = repo.get_issues(**github_filters)

            return [
                self._convert_to_issue_resource(issue, project_id) for issue in issues
            ]
        except GithubException as e:
            raise PlatformError(f"Failed to list issues: {e}", self.platform_name)

    async def list_all_issues(self, **filters) -> List[IssueResource]:
        """List issues across all repositories (global search)."""
        if not self.client:
            await self.authenticate()

        try:
            # Use GitHub's search API for global issue search
            query_parts = []

            # Add state filter
            state = filters.get("state", "open")
            if state != "all":
                query_parts.append(f"state:{state}")

            # Add assignee filter
            if "assignee" in filters:
                assignee = filters["assignee"]
                if assignee == self.username:
                    query_parts.append("assignee:@me")
                else:
                    query_parts.append(f"assignee:{assignee}")

            # Add labels filter
            if "labels" in filters:
                labels = filters["labels"]
                if isinstance(labels, str):
                    labels = [labels]
                for label in labels:
                    query_parts.append(f'label:"{label}"')

            # Add author filter
            if "author" in filters:
                query_parts.append(f"author:{filters['author']}")

            # Default to issues only (not PRs)
            query_parts.append("type:issue")

            query = " ".join(query_parts) if query_parts else "type:issue"

            issues = self.client.search_issues(query)

            return [
                self._convert_to_issue_resource(
                    issue, self._extract_repo_name(issue.repository.full_name)
                )
                for issue in issues
            ]
        except GithubException as e:
            raise PlatformError(f"Failed to search issues: {e}", self.platform_name)

    async def get_issue(
        self, project_id: str, issue_id: str
    ) -> Optional[IssueResource]:
        """Get a specific GitHub issue with comments."""
        if not self.client:
            await self.authenticate()

        try:
            repo = self.client.get_repo(project_id)
            issue = repo.get_issue(int(issue_id))

            # Get issue comments
            try:
                comments = issue.get_comments()
                user_comments = [
                    {
                        "id": str(comment.id),
                        "author": comment.user.login if comment.user else "Unknown",
                        "created_at": comment.created_at,
                        "updated_at": comment.updated_at,
                        "body": comment.body,
                        "system": False,  # GitHub doesn't mark system comments the same way
                    }
                    for comment in comments
                ]

                issue_resource = self._convert_to_issue_resource(issue, project_id)
                if not issue_resource.metadata:
                    issue_resource.metadata = {}
                issue_resource.metadata["comments"] = user_comments
                return issue_resource
            except Exception as e:
                # If getting comments fails, still return the issue without comments
                print(f"Warning: Could not fetch comments for issue {issue_id}: {e}")
                return self._convert_to_issue_resource(issue, project_id)

        except GithubException as e:
            if e.status == 404:
                return None
            raise PlatformError(
                f"Failed to get issue {issue_id}: {e}", self.platform_name
            )

    async def create_issue(
        self, project_id: str, title: str, **kwargs
    ) -> IssueResource:
        """Create a new GitHub issue."""
        if not self.client:
            await self.authenticate()

        try:
            repo = self.client.get_repo(project_id)
            issue_kwargs = {"title": title}

            if "description" in kwargs:
                issue_kwargs["body"] = kwargs["description"]
            if "labels" in kwargs:
                labels = kwargs["labels"]
                if isinstance(labels, str):
                    labels = [labels]
                issue_kwargs["labels"] = labels
            if "assignee" in kwargs:
                issue_kwargs["assignee"] = kwargs["assignee"]

            issue = repo.create_issue(**issue_kwargs)
            return self._convert_to_issue_resource(issue, project_id)
        except GithubException as e:
            raise PlatformError(f"Failed to create issue: {e}", self.platform_name)

    async def update_issue(
        self, project_id: str, issue_id: str, **kwargs
    ) -> IssueResource:
        """Update a GitHub issue."""
        if not self.client:
            await self.authenticate()

        try:
            repo = self.client.get_repo(project_id)
            issue = repo.get_issue(int(issue_id))

            update_kwargs = {}
            if "title" in kwargs:
                update_kwargs["title"] = kwargs["title"]
            if "description" in kwargs:
                update_kwargs["body"] = kwargs["description"]
            if "labels" in kwargs:
                labels = kwargs["labels"]
                if isinstance(labels, str):
                    labels = [labels]
                update_kwargs["labels"] = labels
            if "assignee" in kwargs:
                update_kwargs["assignee"] = kwargs["assignee"]
            if "state_event" in kwargs:
                state_event = kwargs["state_event"]
                if state_event == "close":
                    update_kwargs["state"] = "closed"
                elif state_event == "reopen":
                    update_kwargs["state"] = "open"

            issue.edit(**update_kwargs)
            return self._convert_to_issue_resource(issue, project_id)
        except GithubException as e:
            raise PlatformError(
                f"Failed to update issue {issue_id}: {e}", self.platform_name
            )

    async def close_issue(
        self, project_id: str, issue_id: str, **kwargs
    ) -> IssueResource:
        """Close a GitHub issue."""
        kwargs["state_event"] = "close"
        return await self.update_issue(project_id, issue_id, **kwargs)

    async def create_issue_comment(
        self, project_id: str, issue_id: str, body: str, **kwargs
    ) -> Dict[str, Any]:
        """Create a comment on a GitHub issue."""
        if not self.client:
            await self.authenticate()

        try:
            repo = self.client.get_repo(project_id)
            issue = repo.get_issue(int(issue_id))
            comment = issue.create_comment(body)

            return {
                "id": str(comment.id),
                "author": comment.user.login if comment.user else "Unknown",
                "created_at": comment.created_at.isoformat()
                if comment.created_at
                else None,
                "updated_at": comment.updated_at.isoformat()
                if comment.updated_at
                else None,
                "body": comment.body,
                "url": comment.html_url if hasattr(comment, "html_url") else None,
            }
        except GithubException as e:
            raise PlatformError(f"Failed to create comment: {e}", self.platform_name)

    # Merge Request / Pull Request operations
    async def list_merge_requests(
        self, project_id: str, **filters
    ) -> List[MergeRequestResource]:
        """List pull requests for a GitHub repository."""
        if not self.client:
            await self.authenticate()

        try:
            repo = self.client.get_repo(project_id)
            github_filters = self._normalize_pr_filters(filters)
            prs = repo.get_pulls(**github_filters)

            return [self._convert_to_mr_resource(pr, project_id) for pr in prs]
        except GithubException as e:
            raise PlatformError(
                f"Failed to list pull requests: {e}", self.platform_name
            )

    async def get_merge_request(
        self, project_id: str, mr_id: str
    ) -> Optional[MergeRequestResource]:
        """Get a specific GitHub pull request."""
        if not self.client:
            await self.authenticate()

        try:
            repo = self.client.get_repo(project_id)
            pr = repo.get_pull(int(mr_id))
            return self._convert_to_mr_resource(pr, project_id)
        except GithubException as e:
            if e.status == 404:
                return None
            raise PlatformError(
                f"Failed to get pull request {mr_id}: {e}", self.platform_name
            )

    async def create_merge_request(
        self,
        project_id: str,
        source_branch: str,
        target_branch: str,
        title: str,
        **kwargs,
    ) -> MergeRequestResource:
        """Create a new GitHub pull request with fork support."""
        if not self.client:
            await self.authenticate()

        try:
            # Parse source branch to handle cross-repository references
            source_ref = self.parse_branch_reference(source_branch)
            target_ref = self.parse_branch_reference(target_branch)

            # Determine the target repository
            # For cross-repo PRs, the target is usually the upstream repository
            target_repo_id = project_id

            # Handle cross-repository source branch
            if source_ref["is_cross_repo"]:
                # Source is from a different repository (fork)
                source_head = f"{source_ref['owner']}:{source_ref['branch']}"
                print(f"Debug: GitHub - Creating cross-repo PR from {source_head}")
            else:
                # Source is from the same repository
                source_head = source_ref["branch"]
                print(f"Debug: GitHub - Creating same-repo PR from {source_head}")

            # Handle cross-repository target branch (less common but possible)
            if target_ref["is_cross_repo"]:
                # Target is in a different repository
                target_repo_id = (
                    f"{target_ref['owner']}/{target_ref['branch'].split('/')[0]}"
                )
                target_base = target_ref["branch"]
            else:
                # Target is in the same repository
                target_base = target_ref["branch"]

            # Get the target repository
            target_repo = self.client.get_repo(target_repo_id)

            # Build PR parameters
            pr_kwargs = {
                "title": title,
                "head": source_head,
                "base": target_base,
            }

            # Explicitly handle description parameter to ensure it's included
            if "description" in kwargs:
                pr_kwargs["body"] = kwargs.pop("description")
                print(
                    f"Debug: GitHub - Added description parameter: {pr_kwargs['body'][:100]}..."
                    if len(str(pr_kwargs["body"])) > 100
                    else f"Debug: GitHub - Added description parameter: {pr_kwargs['body']}"
                )

            if "draft" in kwargs:
                pr_kwargs["draft"] = kwargs.pop("draft")
            if "assignee_username" in kwargs:
                # GitHub accepts username directly for assignees
                pr_kwargs["assignee"] = kwargs.pop("assignee_username")

            # Add remaining kwargs
            pr_kwargs.update(kwargs)

            # Debug: Print pull request data
            print(
                f"Creating GitHub pull request with data keys: {list(pr_kwargs.keys())}"
            )
            print(f"Target repo: {target_repo_id}")
            print(f"Head: {pr_kwargs['head']} -> Base: {pr_kwargs['base']}")
            print(f"Description present: {'body' in pr_kwargs}")
            if "body" in pr_kwargs:
                desc_preview = (
                    str(pr_kwargs["body"])[:200] + "..."
                    if len(str(pr_kwargs["body"])) > 200
                    else str(pr_kwargs["body"])
                )
                print(f"Description preview: {desc_preview}")

            # Create the pull request
            pr = target_repo.create_pull(**pr_kwargs)
            return self._convert_to_mr_resource(pr, target_repo_id)
        except ValueError as e:
            # Branch reference parsing error
            raise PlatformError(f"Invalid branch reference: {e}", self.platform_name)
        except GithubException as e:
            raise PlatformError(
                f"Failed to create pull request: {e}", self.platform_name
            )

    async def approve_merge_request(
        self, project_id: str, mr_id: str, **kwargs
    ) -> bool:
        """Approve a GitHub pull request."""
        if not self.client:
            await self.authenticate()

        try:
            repo = self.client.get_repo(project_id)
            pr = repo.get_pull(int(mr_id))

            # Create a review with approval
            review_kwargs = {"event": "APPROVE", "body": kwargs.get("body", "")}
            pr.create_review(**review_kwargs)
            return True
        except GithubException as e:
            raise PlatformError(
                f"Failed to approve pull request {mr_id}: {e}", self.platform_name
            )

    async def merge_merge_request(
        self, project_id: str, mr_id: str, **kwargs
    ) -> MergeRequestResource:
        """Merge a GitHub pull request."""
        if not self.client:
            await self.authenticate()

        try:
            repo = self.client.get_repo(project_id)
            pr = repo.get_pull(int(mr_id))

            merge_kwargs = {}
            if "commit_title" in kwargs:
                merge_kwargs["commit_title"] = kwargs["commit_title"]
            if "commit_message" in kwargs:
                merge_kwargs["commit_message"] = kwargs["commit_message"]
            if "merge_method" in kwargs:
                merge_kwargs["merge_method"] = kwargs["merge_method"]

            pr.merge(**merge_kwargs)
            # Refresh the PR to get updated state
            pr = repo.get_pull(int(mr_id))
            return self._convert_to_mr_resource(pr, project_id)
        except GithubException as e:
            raise PlatformError(
                f"Failed to merge pull request {mr_id}: {e}", self.platform_name
            )

    async def close_merge_request(
        self, project_id: str, mr_id: str, **kwargs
    ) -> MergeRequestResource:
        """Close a GitHub pull request without merging."""
        if not self.client:
            await self.authenticate()

        try:
            repo = self.client.get_repo(project_id)
            pr = repo.get_pull(int(mr_id))

            # Close the pull request by editing its state
            pr.edit(state="closed")

            # Refresh the PR to get updated state
            pr = repo.get_pull(int(mr_id))
            return self._convert_to_mr_resource(pr, project_id)
        except GithubException as e:
            raise PlatformError(
                f"Failed to close pull request {mr_id}: {e}", self.platform_name
            )

    async def update_merge_request(
        self, project_id: str, mr_id: str, **kwargs
    ) -> MergeRequestResource:
        """Update a GitHub pull request (title, description, etc.)."""
        if not self.client:
            await self.authenticate()

        try:
            repo = self.client.get_repo(project_id)
            pr = repo.get_pull(int(mr_id))

            # Prepare update parameters
            update_kwargs = {}
            if "title" in kwargs:
                update_kwargs["title"] = kwargs["title"]
            if "description" in kwargs or "body" in kwargs:
                update_kwargs["body"] = kwargs.get("description", kwargs.get("body"))
            if "state" in kwargs:
                update_kwargs["state"] = kwargs["state"]

            # Apply updates if any parameters provided
            if update_kwargs:
                pr.edit(**update_kwargs)

            # Refresh the PR to get updated state
            pr = repo.get_pull(int(mr_id))
            return self._convert_to_mr_resource(pr, project_id)
        except GithubException as e:
            raise PlatformError(
                f"Failed to update pull request {mr_id}: {e}", self.platform_name
            )

    # Repository operations
    async def list_branches(self, project_id: str, **filters) -> List[Dict[str, Any]]:
        """List branches in a GitHub repository."""
        if not self.client:
            await self.authenticate()

        try:
            repo = self.client.get_repo(project_id)
            branches = repo.get_branches()

            return [
                {
                    "name": branch.name,
                    "commit": {
                        "id": branch.commit.sha,
                        "short_id": branch.commit.sha[:8],
                        "title": branch.commit.commit.message.split("\n")[0],
                        "author_name": branch.commit.commit.author.name
                        if branch.commit.commit.author
                        else None,
                        "created_at": branch.commit.commit.author.date
                        if branch.commit.commit.author
                        else None,
                    },
                    "protected": branch.protected,
                }
                for branch in branches
            ]
        except GithubException as e:
            raise PlatformError(f"Failed to list branches: {e}", self.platform_name)

    async def list_tags(self, project_id: str, **filters) -> List[Dict[str, Any]]:
        """List tags in a GitHub repository."""
        if not self.client:
            await self.authenticate()

        try:
            repo = self.client.get_repo(project_id)
            tags = repo.get_tags()

            return [
                {
                    "name": tag.name,
                    "commit": {
                        "id": tag.commit.sha,
                        "short_id": tag.commit.sha[:8],
                        "title": tag.commit.commit.message.split("\n")[0],
                    },
                    "tarball_url": tag.tarball_url,
                    "zipball_url": tag.zipball_url,
                }
                for tag in tags
            ]
        except GithubException as e:
            raise PlatformError(f"Failed to list tags: {e}", self.platform_name)

    async def list_commits(self, project_id: str, **filters) -> List[Dict[str, Any]]:
        """List commits in a GitHub repository."""
        if not self.client:
            await self.authenticate()

        try:
            repo = self.client.get_repo(project_id)

            # Apply filters
            commit_kwargs = {}
            if "sha" in filters:
                commit_kwargs["sha"] = filters["sha"]
            if "path" in filters:
                commit_kwargs["path"] = filters["path"]
            if "since" in filters:
                commit_kwargs["since"] = filters["since"]
            if "until" in filters:
                commit_kwargs["until"] = filters["until"]

            commits = repo.get_commits(**commit_kwargs)

            return [
                {
                    "id": commit.sha,
                    "short_id": commit.sha[:8],
                    "title": commit.commit.message.split("\n")[0],
                    "message": commit.commit.message,
                    "author_name": commit.commit.author.name
                    if commit.commit.author
                    else None,
                    "author_email": commit.commit.author.email
                    if commit.commit.author
                    else None,
                    "authored_date": commit.commit.author.date
                    if commit.commit.author
                    else None,
                    "committer_name": commit.commit.committer.name
                    if commit.commit.committer
                    else None,
                    "committer_email": commit.commit.committer.email
                    if commit.commit.committer
                    else None,
                    "committed_date": commit.commit.committer.date
                    if commit.commit.committer
                    else None,
                    "web_url": commit.html_url,
                }
                for commit in commits
            ]
        except GithubException as e:
            raise PlatformError(f"Failed to list commits: {e}", self.platform_name)

    # User operations
    async def get_current_user(self) -> Dict[str, Any]:
        """Get current GitHub user information."""
        if not self.client:
            await self.authenticate()

        try:
            user = self.client.get_user()
            return {
                "id": user.id,
                "username": user.login,
                "name": user.name,
                "email": user.email,
                "avatar_url": user.avatar_url,
                "html_url": user.html_url,
                "bio": user.bio,
                "company": user.company,
                "location": user.location,
                "public_repos": user.public_repos,
                "followers": user.followers,
                "following": user.following,
                "created_at": user.created_at,
                "updated_at": user.updated_at,
            }
        except GithubException as e:
            raise PlatformError(f"Failed to get current user: {e}", self.platform_name)

    # Fork operations
    async def create_fork(self, project_id: str, **kwargs) -> ProjectResource:
        """Create a fork of a GitHub repository."""
        if not self.client:
            await self.authenticate()

        try:
            repo = self.client.get_repo(project_id)

            # Extract fork parameters
            fork_kwargs = {}
            if "organization" in kwargs:
                fork_kwargs["organization"] = kwargs["organization"]
            if "name" in kwargs:
                fork_kwargs["name"] = kwargs["name"]
            if "default_branch_only" in kwargs:
                fork_kwargs["default_branch_only"] = kwargs["default_branch_only"]

            # Create the fork
            forked_repo = repo.create_fork(**fork_kwargs)
            return self._convert_to_project_resource(forked_repo)
        except GithubException as e:
            raise PlatformError(
                f"Failed to create fork of {project_id}: {e}", self.platform_name
            )

    async def is_fork(self, project_id: str) -> bool:
        """Check if a GitHub repository is a fork."""
        if not self.client:
            await self.authenticate()

        try:
            repo = self.client.get_repo(project_id)
            return repo.fork
        except GithubException as e:
            if e.status == 404:
                raise ResourceNotFoundError(
                    "repository", project_id, self.platform_name
                )
            raise PlatformError(
                f"Failed to check fork status for {project_id}: {e}", self.platform_name
            )

    async def get_fork_parent(self, project_id: str) -> Optional[str]:
        """Get the parent repository ID of a GitHub fork."""
        if not self.client:
            await self.authenticate()

        try:
            repo = self.client.get_repo(project_id)
            if repo.fork and repo.parent:
                return repo.parent.full_name
            return None
        except GithubException as e:
            if e.status == 404:
                raise ResourceNotFoundError(
                    "repository", project_id, self.platform_name
                )
            raise PlatformError(
                f"Failed to get fork parent for {project_id}: {e}", self.platform_name
            )

    async def get_merge_request_diff(
        self, project_id: str, mr_id: str, **options
    ) -> Dict[str, Any]:
        """Get diff/changes for a GitHub pull request."""
        if not self.client:
            await self.authenticate()

        try:
            repo = self.client.get_repo(project_id)
            pr = repo.get_pull(int(mr_id))

            # Get diff format option (default: json)
            diff_format = options.get("format", "json")
            include_diff = options.get("include_diff", True)

            # Get files changed in the PR
            files = list(pr.get_files())

            # Initialize response structure
            response = {
                "mr_id": str(mr_id),
                "total_changes": {
                    "additions": pr.additions,
                    "deletions": pr.deletions,
                    "files_changed": len(files),
                },
                "files": [],
                "diff_format": diff_format,
                "truncated": False,
            }

            # Process file changes
            for file in files:
                file_info = {
                    "path": file.filename,
                    "status": file.status,  # GitHub provides: added, removed, modified, renamed
                    "additions": file.additions,
                    "deletions": file.deletions,
                    "binary": file.filename.endswith(
                        (".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip", ".exe")
                    ),
                }

                # Include diff content if requested and file is not too large
                if (
                    include_diff
                    and not file_info["binary"]
                    and hasattr(file, "patch")
                    and file.patch
                ):
                    file_info["diff"] = file.patch

                response["files"].append(file_info)

            return response

        except GithubException as e:
            if e.status == 404:
                raise ResourceNotFoundError("pull_request", mr_id, self.platform_name)
            raise PlatformError(
                f"Failed to get pull request diff {mr_id}: {e}", self.platform_name
            )

    async def get_merge_request_commits(
        self, project_id: str, mr_id: str, **filters
    ) -> Dict[str, Any]:
        """Get commits for a GitHub pull request."""
        if not self.client:
            await self.authenticate()

        try:
            repo = self.client.get_repo(project_id)
            pr = repo.get_pull(int(mr_id))

            # Get commits from the pull request
            commits = list(pr.get_commits())

            response: Dict[str, Any] = {
                "mr_id": str(mr_id),
                "total_commits": len(commits),
                "commits": [],
            }

            # Process each commit
            for commit in commits:
                commit_info = {
                    "sha": commit.sha,
                    "message": commit.commit.message,
                    "author": commit.commit.author.name if commit.commit.author else "",
                    "authored_date": commit.commit.author.date.isoformat()
                    if commit.commit.author and commit.commit.author.date
                    else "",
                    "committer": commit.commit.committer.name
                    if commit.commit.committer
                    else "",
                    "committed_date": commit.commit.committer.date.isoformat()
                    if commit.commit.committer and commit.commit.committer.date
                    else "",
                    "url": commit.html_url,
                }

                # Add stats if available (GitHub provides these)
                if hasattr(commit, "stats") and commit.stats:
                    commit_info["additions"] = commit.stats.additions
                    commit_info["deletions"] = commit.stats.deletions

                response["commits"].append(commit_info)

            return response

        except GithubException as e:
            if e.status == 404:
                raise ResourceNotFoundError("pull_request", mr_id, self.platform_name)
            raise PlatformError(
                f"Failed to get pull request commits {mr_id}: {e}", self.platform_name
            )

    def parse_branch_reference(self, branch_ref: str) -> Dict[str, Any]:
        """Parse GitHub branch reference into components.

        Args:
            branch_ref: Branch reference in format 'branch' or 'owner:branch'

        Returns:
            Dict with keys: 'owner' (optional), 'branch', 'is_cross_repo'
        """
        if ":" in branch_ref:
            # Cross-repository reference: 'owner:branch'
            parts = branch_ref.split(":", 1)
            if len(parts) != 2:
                raise ValueError(f"Invalid branch reference format: {branch_ref}")

            owner, branch = parts
            if not owner or not branch:
                raise ValueError(f"Invalid branch reference format: {branch_ref}")

            return {"owner": owner, "branch": branch, "is_cross_repo": True}  # type: ignore[dict-item]
        else:
            # Same-repository reference: 'branch'
            if not branch_ref:
                raise ValueError("Branch reference cannot be empty")

            return {"branch": branch_ref, "is_cross_repo": False}  # type: ignore[dict-item]

    # Helper methods
    def _convert_to_project_resource(self, repo) -> ProjectResource:
        """Convert GitHub repository to ProjectResource."""
        return ProjectResource(
            id=repo.full_name,  # Use full_name (owner/repo) as ID
            title=repo.name,
            platform=self.platform_name,
            resource_type=ResourceType.PROJECT,
            url=repo.html_url,
            namespace=repo.owner.login,
            visibility="private" if repo.private else "public",
            default_branch=repo.default_branch,
            clone_url_http=repo.clone_url,
            clone_url_ssh=repo.ssh_url,
            description=repo.description,
            created_at=repo.created_at,
            updated_at=repo.updated_at,
            metadata={
                "id": repo.id,
                "full_name": repo.full_name,
                "owner": repo.owner.login,
                "private": repo.private,
                "fork": repo.fork,
                "archived": repo.archived,
                "disabled": repo.disabled,
                "stars": repo.stargazers_count,
                "forks": repo.forks_count,
                "language": repo.language,
                "has_issues": repo.has_issues,
                "has_projects": repo.has_projects,
                "has_wiki": repo.has_wiki,
            },
        )

    def _convert_to_issue_resource(self, issue, project_id: str) -> IssueResource:
        """Convert GitHub issue to IssueResource."""
        return IssueResource(
            id=str(issue.number),
            title=issue.title,
            platform=self.platform_name,
            resource_type=ResourceType.ISSUE,
            url=issue.html_url,
            state=ResourceState.OPENED
            if issue.state == "open"
            else ResourceState.CLOSED,
            project_id=project_id,
            description=issue.body,
            author=issue.user.login if issue.user else None,
            assignee=issue.assignee.login if issue.assignee else None,
            labels=[label.name for label in issue.labels],
            created_at=issue.created_at,
            updated_at=issue.updated_at,
            milestone=issue.milestone.title if issue.milestone else None,
            metadata={
                "id": issue.id,
                "number": issue.number,
                "locked": issue.locked,
                "comments_count": issue.comments,
                "repository": project_id,
                "pull_request": hasattr(issue, "pull_request")
                and issue.pull_request is not None,
            },
        )

    def _convert_to_mr_resource(self, pr, project_id: str) -> MergeRequestResource:
        """Convert GitHub pull request to MergeRequestResource."""
        state = ResourceState.OPENED
        if pr.state == "closed":
            state = ResourceState.CLOSED
        elif pr.merged:
            state = ResourceState.MERGED

        return MergeRequestResource(
            id=str(pr.number),
            title=pr.title,
            platform=self.platform_name,
            resource_type=ResourceType.MERGE_REQUEST,
            url=pr.html_url,
            state=state,
            project_id=project_id,
            source_branch=pr.head.ref,
            target_branch=pr.base.ref,
            description=pr.body,
            author=pr.user.login if pr.user else None,
            assignee=pr.assignee.login if pr.assignee else None,
            labels=[label.name for label in pr.labels],
            created_at=pr.created_at,
            updated_at=pr.updated_at,
            merge_commit_sha=pr.merge_commit_sha,
            draft=pr.draft,
            metadata={
                "id": pr.id,
                "number": pr.number,
                "merged": pr.merged,
                "merged_at": pr.merged_at,
                "mergeable": pr.mergeable,
                "mergeable_state": pr.mergeable_state,
                "comments_count": pr.comments,
                "review_comments_count": pr.review_comments,
                "commits_count": pr.commits,
                "additions": pr.additions,
                "deletions": pr.deletions,
                "changed_files": pr.changed_files,
            },
        )

    def _normalize_issue_filters(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize issue filters to GitHub format."""
        github_filters = {}

        filter_mapping = {
            "state": "state",
            "labels": "labels",
            "assignee": "assignee",
            "creator": "creator",
            "mentioned": "mentioned",
            "milestone": "milestone",
            "sort": "sort",
            "direction": "direction",
        }

        for key, value in filters.items():
            if key in filter_mapping:
                if key == "state" and value == "opened":
                    github_filters["state"] = "open"
                elif key == "labels":
                    if isinstance(value, str):
                        github_filters["labels"] = [value]  # type: ignore
                    else:
                        github_filters["labels"] = value
                else:
                    github_filters[filter_mapping[key]] = value

        return github_filters

    def _normalize_global_issue_filters(
        self, filters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Normalize issue filters for global search."""
        return filters  # Search query is built differently for global search

    def _normalize_pr_filters(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize pull request filters to GitHub format."""
        github_filters = {}

        filter_mapping = {
            "state": "state",
            "head": "head",
            "base": "base",
            "sort": "sort",
            "direction": "direction",
        }

        for key, value in filters.items():
            if key in filter_mapping:
                if key == "state":
                    if value == "opened":
                        github_filters["state"] = "open"
                    elif value == "merged":
                        # GitHub doesn't have a direct "merged" state filter
                        # We'll need to filter merged PRs after fetching
                        github_filters["state"] = "closed"
                    else:
                        github_filters["state"] = value
                else:
                    github_filters[filter_mapping[key]] = value

        return github_filters

    def _extract_repo_name(self, full_name: str) -> str:
        """Extract repository name from full name (owner/repo)."""
        return full_name

    def _parse_datetime(self, date_obj) -> Optional[datetime]:
        """Parse GitHub datetime object."""
        if isinstance(date_obj, datetime):
            return date_obj
        return None
