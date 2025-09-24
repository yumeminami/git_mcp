# Issue Analysis Command

Analyze GitLab/GitHub issues using git_mcp_server MCP tools for comprehensive issue understanding and implementation planning.

**Arguments:** $ARGUMENTS

Please analyze this thoroughly and in great detail, considering multiple perspectives on the issue requirements and broader project context.

## Mode Selection

If no arguments provided, show **My Issues Dashboard**:
- List issues assigned to me across configured platforms
- Show priority, status, and project context
- Allow selection for detailed analysis

If arguments provided, analyze **Specific Issue**:

## Issue Documentation Management

**First, handle issue documentation:**

1. **Extract Issue ID** from URL or direct ID argument
   - For GitHub URLs: extract number from `/issues/123` or `/pull/456`
   - For GitLab URLs: extract from `/-/issues/123` or `/-/merge_requests/456`
   - For direct ID: use as-is

2. **Check for Existing Documentation**
   - Look for `.claude/issue-<ISSUE_ID>-<sanitized-title>.md` in current project
   - If exists: Read existing analysis and show summary of previous work
   - If not exists: Will create new documentation file
   - **Note:** Add `.claude/issue-*.md` to `.gitignore` to keep docs local, or commit them for team sharing

3. **Create/Update Issue Document** with structure:
   ```markdown
   # Issue #<ID>: <Title>

   **URL:** <issue_url>
   **Status:** <status>
   **File:** issue-<ID>-<sanitized-title>.md
   **Created:** <timestamp>
   **Last Updated:** <timestamp>

   ## 🎯 Issue Analysis (Updated: <timestamp>)
   [Analysis content]

   ## 📋 Development Plan (Updated: <timestamp>)
   [Plan content - added by /plan]

   ## 🔨 Implementation Progress (Updated: <timestamp>)
   [Implementation notes - added by /implement]

   ## 🧪 Testing Status (Updated: <timestamp>)
   [Test results - added by /test]

   ## 📚 Documentation Updates (Updated: <timestamp>)
   [Doc changes - added by /doc]

   ## 🚀 Pull Request (Updated: <timestamp>)
   [PR details - added by /pr]
   ```

**Then perform issue analysis:**
- Fetch issue details from URL or platform/project/issue-id
- Provide technical analysis and requirements
- Generate implementation suggestions
- Save analysis to issue documentation file

## Analysis Output

**For My Issues List:**
1. **Assigned Issues** - use `mcp__git-mcp-server__list_my_issues()` to get issues assigned to current user
2. **Recent Activity** - use `mcp__git-mcp-server__list_all_issues()` for recently updated issues
3. **Priority Issues** - filter high priority or urgent items
4. **Selection Prompt** - choose issue for detailed analysis with `mcp__git-mcp-server__get_issue_details()`

**For Specific Issue:**
1. **Issue Overview** - use `mcp__git-mcp-server__get_issue_by_url()` or `mcp__git-mcp-server__get_issue_details()` for title, description, labels, priority
2. **Technical Requirements** - analyze what needs to be implemented, considering potential challenges and edge cases
3. **Context Analysis** - review current codebase for related components and dependencies
4. **Next Steps** - evaluate multiple approaches for development, showing complete reasoning for the recommended solution

Use `/plan` after issue analysis to generate the development plan.

## Available MCP Tools

- `mcp__git-mcp-server__get_issue_by_url` - Fetch issue details from URL
- `mcp__git-mcp-server__get_issue_details` - Get issue details by platform/project/ID
- `mcp__git-mcp-server__list_my_issues` - List issues assigned to current user
- `mcp__git-mcp-server__list_all_issues` - List recent issues across platforms
- `mcp__git-mcp-server__list_issues` - List issues in specific project
