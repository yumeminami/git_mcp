# Documentation Updates

Update project documentation, README files, and inline code comments to reflect implementation changes and provide comprehensive user guidance.

**Focus:** $ARGUMENTS

## Issue Documentation Update

**First, update issue documentation:**

1. **Find Issue Document** - Look for `.claude/issue-*.md` files in current project
   - Read existing implementation and testing progress
   - If no issue doc exists, suggest running `/issue` and `/plan` first

2. **Track Documentation Progress** in the issue document:
   - Update `## 📚 Documentation Updates (Updated: <timestamp>)` section
   - Document what files were updated
   - Record documentation decisions and approach
   - Note any new user guides or API docs created

## Documentation Strategy

Update comprehensive project documentation:

1. **README Updates** - reflect new features, installation steps, usage examples
2. **API Documentation** - document new functions, classes, and methods
3. **User Guides** - create step-by-step instructions for new functionality
4. **Code Comments** - add inline documentation for complex logic
5. **Architecture Docs** - update system design documentation

## Documentation Types

**README.md Updates:**
- Add new features to feature list
- Update installation instructions
- Add usage examples and workflows
- Update configuration options
- Add troubleshooting section

**API Documentation:**
- Document new functions and classes
- Add parameter descriptions and types
- Include return value documentation
- Provide usage examples
- Document error conditions

**User Guides:**
- Create step-by-step tutorials
- Add configuration guides
- Include best practices
- Provide troubleshooting tips

**Code Comments:**
- Document complex algorithms
- Explain design decisions
- Add type hints and docstrings
- Document configuration options

## Best Practices

- Write clear, concise documentation
- Include practical examples and use cases
- Keep documentation up-to-date with code changes
- Use consistent formatting and style
- Include screenshots or diagrams where helpful
- Consider different user skill levels

Use `mcp__git-mcp-server__get_project_details()` to understand current documentation structure.

## Documentation Review

Ensure documentation covers:

1. **Installation** - clear setup instructions
2. **Configuration** - all configuration options explained
3. **Usage** - practical examples and workflows
4. **API Reference** - complete function and class documentation
5. **Troubleshooting** - common issues and solutions
6. **Contributing** - guidelines for contributors
7. **Changelog** - record of changes and updates

**After documentation updates, finalize with `/pr` to create pull request.**

Use `/pr <issue-id>` after documentation is complete.

## Available MCP Tools

- `mcp__git-mcp-server__get_project_details` - Understand project structure
- `mcp__git-mcp-server__get_issue_details` - Reference issue requirements for documentation
- `mcp__git-mcp-server__create_issue_comment` - Add documentation progress updates
