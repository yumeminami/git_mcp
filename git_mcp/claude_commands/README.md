# Git MCP Issue-to-Code Workflow

These slash commands provide a complete issue-driven development workflow, integrated with our Git MCP server for automated development processes.

**Command Type:** User-level commands (available across all projects)
**Installation Location:** `~/.claude/commands/`

## 🚀 Complete Workflow

```bash
# 1. Analyze issue (GitLab or GitHub)
/issue https://gitlab.com/group/project/-/issues/123
# or
/issue https://github.com/user/repo/issues/456

# 2. Generate development plan
/plan

# 3. Implement functionality
/implement

# 4. Write tests
/test

# 5. Update documentation
/doc

# 6. Create PR/MR
/pr 123
```

## 📋 Command Details

### `/issue` - Issue Analysis
- No arguments: Show my assigned issues list
- With arguments: Get specific issue details from GitLab/GitHub URL
- Analyze technical requirements and context
- Provide implementation suggestions

### `/plan` - Development Planning
- Generate development plan based on issue analysis
- Analyze current codebase structure
- Provide branch strategy and implementation steps

### `/implement` - Functionality Implementation
- Implement planned functionality
- Create feature branch
- Write high-quality code following project conventions

### `/test` - Test Generation
- Generate tests for implemented functionality
- Include unit tests, integration tests
- Handle edge cases and error scenarios

### `/doc` - Documentation Updates
- Update API documentation
- Add usage examples
- Update README and configuration guides

### `/pr` - Create PR/MR
- Commit code and push branch
- Create Pull Request or Merge Request
- Automatically link and close related issue

## 🛠️ Integration Features

### MCP Tools Integration
These commands leverage our Git MCP server tools:
- `get_issue_by_url()` - Parse URL and fetch issue
- `get_issue_details()` - Get detailed information
- `create_merge_request()` - Create MR
- `get_platform_config()` - Get configuration info

Start your automated issue-to-code development journey! 🚀
