---
description: Create pull/merge request and close related issue
argument-hint: [issue-id] [optional: target-branch]
allowed-tools: Bash(git *), mcp__git-mcp-server__*
---

# 🚀 Pull Request Creation

Analyze the changes made thoroughly and consider multiple ways to present them clearly and effectively in the pull/merge request.

**Issue ID:** $ARGUMENTS

## Issue Documentation Finalization

**First, finalize issue documentation:**

1. **Find Issue Document** - Look for `.claude/issue-$ARGUMENTS-*.md` in current project
   - Use the provided issue ID to find the correct documentation file
   - If no issue doc exists, create a summary from available git history

2. **Final Update** to the issue document:
   - Update `## 🚀 Pull Request (Updated: <timestamp>)` section
   - Include PR/MR URL, title, and description
   - Summarize all work completed (analysis → plan → implementation → testing → docs → PR)
   - Mark issue as completed
   - Archive or mark for cleanup

## PR Creation Process

1. **Prepare Branch**
   !git add related-resources
   !git status
   !git commit -m "Implement feature for issue #$ARGUMENTS"
   !git push -u origin HEAD

2. **Fork Detection and Repository Analysis**
   - Use `get_fork_info()` to check if current repository is a fork
   - If it's a fork, identify the upstream repository for PR creation
   - Determine the correct target repository (fork vs upstream)

3. **Push to Remote**
   !git push -u origin HEAD

4. **Create Pull/Merge Request with Fork Support**
   Use `create_merge_request()` to create the PR/MR with enhanced fork support:

   **For Fork-to-Upstream PRs:**
   - Source branch: `username:branch-name` format (automatically detected)
   - Target repository: Upstream repository (parent)
   - Target branch: Usually `main` or `master`

   **For Same-Repository PRs:**
   - Source branch: `branch-name` format (current behavior)
   - Target repository: Current repository
   - Target branch: As specified or default

   **PR Parameters:**
   - Craft a descriptive title linking to issue
   - Create comprehensive description that clearly explains the solution
   - **IMPORTANT**: In the description, use the full issue URL from `.claude/issue-$ARGUMENTS-*.md` instead of just `#$ARGUMENTS`
   - Extract the URL using: `grep "URL:" .claude/issue-$ARGUMENTS-*.md | head -1 | cut -d' ' -f2`
   - Consider appropriate labels and reviewers

5. **Fork Workflow Examples**

   **Example 1: GitHub Fork-to-Upstream PR**
   ```
   # Check if current repo is a fork
   get_fork_info("github", "myuser/upstream-project")

   # If it's a fork, create PR to upstream
   create_merge_request(
       platform="github",
       project_id="upstream-owner/upstream-project",  # Target upstream repo
       source_branch="myuser:feature-branch",         # Fork branch reference
       target_branch="main",                          # Upstream main branch
       title="Fix issue #123: Add new feature",
       description="Implements feature as requested in issue..."
   )
   ```

   **Example 2: GitLab Fork-to-Upstream MR**
   ```
   # Check if current repo is a fork
   get_fork_info("gitlab", "456")  # Fork project ID

   # If it's a fork, create MR to upstream
   create_merge_request(
       platform="gitlab",
       project_id="456",                              # Fork project ID (source)
       source_branch="feature-branch",                # Simple branch name
       target_branch="main",                          # Upstream main branch
       target_project_id="123",                       # Upstream project ID (target)
       title="Fix issue #123: Add new feature",
       description="Implements feature as requested in issue..."
   )
   ```

   **Example 3: Same-Repository PR/MR (existing behavior)**
   ```
   create_merge_request(
       platform="github",  # or "gitlab"
       project_id="myuser/my-project",  # or GitLab project ID
       source_branch="feature-branch",                # Simple branch name
       target_branch="main",
       title="Fix issue #123: Add new feature",
       description="Implements feature as requested in issue..."
   )
   ```

6. **PR Description Template**
   ```
   ## Summary
   Implements [feature description] as requested in issue #$ARGUMENTS

   ## Changes Made
   - [List of changes]

   ## Testing
   - [Test coverage details]

   ## Documentation
   - [Documentation updates]

   Closes #$ARGUMENTS
   ```

7. **Available Fork MCP Tools**

   **New Tools for Fork Management:**
   - `create_fork(platform, project_id, **kwargs)` - Create a fork of a repository
   - `get_fork_info(platform, project_id)` - Check fork status and get parent info
   - `list_forks(platform, project_id)` - List forks of a repository (basic implementation)

   **Enhanced Existing Tools:**
   - `create_merge_request()` - Now supports cross-repository PRs with `owner:branch` format
   - All existing MCP tools work seamlessly with fork workflows

8. **Final Steps**
   - Link PR to original issue (use `update_issue()` to close issue if needed)
   - Request code review via `get_merge_request_details()` for tracking
   - Monitor CI/CD pipeline
   - Address review feedback

9. **Complete Issue Documentation**
   - Save final PR details to `.claude/issue-$ARGUMENTS-*.md`
   - Mark workflow as completed in the documentation
   - Issue document now serves as complete project history for this feature

**Workflow Complete!** From issue analysis to PR creation with full documentation trail.
