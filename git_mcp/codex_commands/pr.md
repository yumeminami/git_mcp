# Pull Request Creation

Create and manage pull requests for completed feature development, ensuring proper review process and integration with the main codebase.

**Focus:** $ARGUMENTS

## Issue Documentation Update

**First, update issue documentation:**

1. **Review Changes** - Check what was implemented and needs to be merged
2. **Prepare PR Details** - Create simple summary of changes

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
Fixes #<issue-number>

[Brief summary of changes]
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

**Verify PR was created successfully.**

## Available MCP Tools

- `mcp__git-mcp-server__create_merge_request` - Create pull request
- `mcp__git-mcp-server__get_project_details` - Get project information
- `mcp__git-mcp-server__get_issue_details` - Reference issue for PR linking
- `mcp__git-mcp-server__list_merge_requests` - Check existing PRs
- `mcp__git-mcp-server__get_merge_request_details` - Get PR information
- `mcp__git-mcp-server__update_issue` - Update issue status when PR is created
