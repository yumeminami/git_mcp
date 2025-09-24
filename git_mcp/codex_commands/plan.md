# Development Plan Generator

Consider multiple architectural approaches and evaluate their tradeoffs deeply before generating a structured development plan.

**Context:** $ARGUMENTS

## Issue Documentation Update

**First, update issue documentation:**

1. **Find Issue Document** - Look for `.claude/issue-*.md` files in current project
   - If multiple exist, prompt user to specify which issue this plan is for
   - If none exist, suggest running `/issue <issue-url>` first for proper documentation

2. **Update Plan Section** in the issue document:
   - Replace/append to `## 📋 Development Plan (Updated: <timestamp>)` section
   - Include full plan details with timestamp
   - Preserve other sections (analysis, implementation, testing, etc.)

## Plan Generation

Create a comprehensive development plan including:

1. **Branch Strategy** - determine optimal branch name and workflow approach
2. **File Structure** - analyze what files need to be created/modified and their relationships
3. **Implementation Steps** - provide ordered task breakdown with clear dependencies
4. **Testing Strategy** - design comprehensive test coverage plan
5. **Documentation Updates** - identify README, docs, and comment requirements

Use `mcp__git-mcp-server__get_project_details()` to understand project structure and `mcp__git-mcp-server__list_merge_requests()` to review existing workflow patterns.

## Platform API Planning

**When planning platform integrations**, consult the API documentation in CLAUDE.md:

**GitLab API Resources:**
- API Objects: https://python-gitlab.readthedocs.io/en/stable/api-objects.html
- Usage Patterns: https://python-gitlab.readthedocs.io/en/stable/gl_objects/

**GitHub API Resources:**
- Examples: https://pygithub.readthedocs.io/en/stable/examples.html
- API Reference: https://pygithub.readthedocs.io/en/stable/github_objects.html

**Consider API limitations and capabilities when planning:**
- Rate limiting requirements
- Authentication scopes needed
- Available operations and data structures
- Error handling patterns

## Repository Context

Analyze current repository structure:

!git branch -a
!git status
!find . -name "*.py" -o -name "*.js" -o -name "*.ts" | head -20

Based on the issue requirements and current codebase, thoroughly evaluate potential approaches and provide a detailed implementation roadmap with clear rationale for the chosen approach.

**After generating the plan, save it to the issue documentation file.**

Use `/implement` to start coding based on this plan.

## Available MCP Tools

- `mcp__git-mcp-server__get_project_details` - Get project information
- `mcp__git-mcp-server__list_merge_requests` - Review existing MR patterns
- `mcp__git-mcp-server__list_projects` - List available projects
- `mcp__git-mcp-server__get_issue_details` - Reference issue details for planning
