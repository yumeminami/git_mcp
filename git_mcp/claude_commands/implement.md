---
description: Implement planned functionality with best practices using git_mcp_server tools
argument-hint: [optional specific component or step]
allowed-tools: mcp__git-mcp-server__*
---

# 🔨 Implementation

Please implement the planned functionality thoroughly and in great detail, considering multiple approaches and potential edge cases throughout the development process.

**Focus:** $ARGUMENTS

## Issue Documentation Update

**First, update issue documentation:**

1. **Find Issue Document** - Look for `.claude/issue-*.md` files in current project
   - Read existing plan and analysis to understand requirements
   - If no issue doc exists, suggest running `/issue` and `/plan` first

2. **Track Implementation Progress** in the issue document:
   - Update `## 🔨 Implementation Progress (Updated: <timestamp>)` section
   - Document what files were modified/created
   - Record implementation decisions and rationale
   - Note any deviations from the original plan
   - Track completion status of each implementation step

## Implementation Process

1. **Create Feature Branch** - based on development plan
2. **Code Implementation** - design optimal code structure and write high-quality, maintainable code
3. **Follow Conventions** - match existing code style and patterns
4. **Error Handling** - anticipate edge cases and implement robust error handling
5. **Code Comments** - add necessary documentation for complex logic

## Best Practices

- Follow existing project patterns and conventions
- Write clean, readable, and maintainable code
- Implement proper error handling and logging
- Add type hints and documentation
- Consider security implications

Use `get_project_details()` to understand codebase structure and `list_merge_requests()` to review implementation patterns in recent changes.

## Platform API Resources

**When implementing platform-specific features**, refer to the API documentation in CLAUDE.md:

**For GitLab integrations** (`git_mcp/platforms/gitlab.py`):
- **API Objects Reference**: https://python-gitlab.readthedocs.io/en/stable/api-objects.html
- **Usage Examples**: https://python-gitlab.readthedocs.io/en/stable/gl_objects/

**For GitHub integrations** (`git_mcp/platforms/github.py`):
- **Examples & Patterns**: https://pygithub.readthedocs.io/en/stable/examples.html
- **API Reference**: https://pygithub.readthedocs.io/en/stable/github_objects.html

**Common use cases requiring API docs:**
- Extending platform adapter methods
- Adding new MCP tools for platform operations
- Implementing custom issue/PR workflows
- Debugging API response handling

**After implementation, update the issue documentation with progress and file changes.**

Use `/test` after implementation to generate comprehensive tests.
