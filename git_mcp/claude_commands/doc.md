---
description: Update documentation and API docs using git_mcp_server tools for project context
argument-hint: [optional doc type or component focus]
allowed-tools: mcp__git-mcp-server__*
---

# 📚 Documentation Update

Evaluate what documentation needs updating and consider multiple ways to make it most helpful for users throughout the update process.

**Focus:** $ARGUMENTS

## Issue Documentation Update

**First, update issue documentation:**

1. **Review Changes** - Identify what documentation needs updating
2. **Plan Documentation Updates** - Determine scope and priorities

## Documentation Updates

1. **API Documentation** - update function/method documentation clearly and comprehensively
2. **README Updates** - enhance usage examples and feature descriptions
3. **Configuration Guide** - update setup and configuration docs as needed
4. **Examples** - add practical, helpful usage examples
5. **Changelog** - document changes and improvements comprehensively

## Documentation Types

- **Code Comments** - inline documentation for complex logic
- **Docstrings** - comprehensive function/class documentation
- **README** - user-facing documentation and examples
- **API Docs** - detailed API reference
- **Configuration** - setup and configuration guides

Use `get_project_details()` to understand documentation structure and `list_merge_requests()` to review recent documentation patterns.

Use `/pr` after documentation to create the pull/merge request.
