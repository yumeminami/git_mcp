# Test Generation and Execution

Generate comprehensive tests and validate implementation quality through automated testing, linting, and quality checks.

**Focus:** $ARGUMENTS

## Issue Documentation Update

**First, update issue documentation:**

1. **Find Issue Document** - Look for `.claude/issue-*.md` files in current project
   - Read existing implementation progress to understand what was built
   - If no issue doc exists, suggest running `/issue` and `/plan` first

2. **Track Testing Progress** in the issue document:
   - Update `## 🧪 Testing Status (Updated: <timestamp>)` section
   - Document test coverage and results
   - Record any test failures and fixes applied
   - Note testing strategy and validation approach

## Testing Strategy

Create comprehensive test coverage including:

1. **Unit Tests** - test individual functions and methods in isolation
2. **Integration Tests** - test component interactions and workflows
3. **End-to-End Tests** - test complete user workflows
4. **Code Quality** - run linting, formatting, and type checking
5. **Security Tests** - validate security best practices

## Test Implementation

1. **Analyze Codebase** - understand existing test patterns and frameworks
2. **Generate Test Cases** - create comprehensive test scenarios covering:
   - Happy path scenarios
   - Edge cases and error conditions
   - Input validation
   - Error handling
   - Integration points

3. **Run Test Suite** - execute all tests and report results
4. **Quality Checks** - run linting, formatting, and security scans
5. **Coverage Analysis** - ensure adequate test coverage

## Best Practices

- Follow existing test patterns and conventions
- Write clear, maintainable test cases
- Include both positive and negative test scenarios
- Test error conditions and edge cases
- Validate input/output behavior
- Use appropriate test fixtures and mocking

Use `mcp__git-mcp-server__get_project_details()` to understand project structure and existing test frameworks.

## Quality Validation

Run comprehensive quality checks:

```bash
# Python projects
pytest --cov=module --cov-report=term-missing
ruff check .
ruff format .
mypy .
bandit -r .

# Node.js projects
npm test
npm run lint
npm run format
npm run type-check

# General
pre-commit run --all-files
```

**After testing, update the issue documentation with test results and coverage metrics.**

Use `/doc` after successful testing to update documentation.

## Available MCP Tools

- `mcp__git-mcp-server__get_project_details` - Understand project structure
- `mcp__git-mcp-server__get_issue_details` - Reference issue requirements for test scenarios
- `mcp__git-mcp-server__create_issue_comment` - Report test results on issues
