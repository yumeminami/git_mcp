# Pull Request Creation

Create and manage pull requests for completed feature development, ensuring proper review process and integration with the main codebase.

**Focus:** $ARGUMENTS

## Issue Documentation Update

**First, update issue documentation:**

1. **Find Issue Document** - Look for `.claude/issue-*.md` files in current project
   - Read complete implementation history and progress
   - If no issue doc exists, suggest running `/issue` first

2. **Complete PR Section** in the issue document:
   - Update `## 🚀 Pull Request (Updated: <timestamp>)` section
   - Document PR creation and details
   - Include PR URL and status
   - Record review process and feedback

## Pull Request Strategy

Create comprehensive pull request with proper process:

1. **Pre-PR Checklist** - ensure readiness for review
2. **Branch Preparation** - clean up commits and push changes
3. **PR Creation** - create detailed pull request with proper description
4. **Review Process** - manage review feedback and iterations
5. **Merge Strategy** - handle final merge when approved

## Pre-PR Validation

Before creating PR, validate:

**Code Quality:**
- All tests passing
- Linting and formatting clean
- Type checking successful
- Security scans clean

**Documentation:**
- README updated
- API docs complete
- Code comments added
- User guides created

**Git Hygiene:**
- Commits are clean and descriptive
- Branch is up-to-date with main
- No merge conflicts
- Proper commit message format

## PR Creation Process

1. **Analyze Changes** - review all modified files and changes
2. **Generate PR Summary** - create comprehensive description including:
   - Feature overview and purpose
   - Technical implementation details
   - Testing approach and results
   - Documentation updates
   - Breaking changes (if any)

3. **Create Pull Request** using MCP tools:
   - Use `mcp__git-mcp-server__create_merge_request()`
   - Include proper title following project conventions
   - Add detailed description with sections:
     - ## Summary
     - ## Changes Made
     - ## Testing
     - ## Documentation
     - ## Review Notes

4. **Link to Issue** - reference original issue in PR description

## PR Template

```markdown
## Summary
Brief description of the feature/fix and its purpose.

## Changes Made
- Detailed list of changes
- New files created
- Modified functionality
- Dependencies added

## Testing
- Test coverage added
- All tests passing
- Manual testing performed
- Quality checks completed

## Documentation
- README updated
- API docs added
- User guides created
- Code comments added

## Review Notes
- Specific areas needing attention
- Design decisions made
- Potential concerns
- Future improvements

Closes #<issue-number>
```

## Post-PR Management

**Review Process:**
- Respond to reviewer feedback
- Make requested changes
- Update PR description as needed
- Ensure CI/CD passes

**Final Steps:**
- Merge when approved
- Clean up feature branch
- Update issue status
- Communicate completion

**After PR creation, update issue documentation with PR details and URL.**

## Available MCP Tools

- `mcp__git-mcp-server__create_merge_request` - Create pull request
- `mcp__git-mcp-server__get_project_details` - Get project information
- `mcp__git-mcp-server__get_issue_details` - Reference issue for PR linking
- `mcp__git-mcp-server__list_merge_requests` - Check existing PRs
- `mcp__git-mcp-server__get_merge_request_details` - Get PR information
- `mcp__git-mcp-server__update_issue` - Update issue status when PR is created
