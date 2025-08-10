---
description: Generate comprehensive test suites using git_mcp_server tools for project context
argument-hint: [optional test type or component focus]
allowed-tools: mcp__git-mcp-server__*
---

# 🧪 Test Generation

Think harder about test coverage and potential failure scenarios before generating comprehensive test suites for implemented functionality.

**Focus:** $ARGUMENTS

## Test Strategy

1. **Unit Tests** - think about testing individual functions and methods thoroughly
2. **Integration Tests** - think more about component interactions and dependencies
3. **Edge Cases** - think harder about boundary conditions and error scenarios
4. **Mock External Dependencies** - isolate components for testing
5. **Test Coverage** - think about ensuring comprehensive coverage across all code paths

## Test Types

- **Happy Path Tests** - normal operation scenarios
- **Error Handling Tests** - exception and error conditions
- **Boundary Tests** - edge cases and limits
- **Integration Tests** - component interactions
- **Performance Tests** - if applicable

Use `get_project_details()` to understand testing frameworks and `list_merge_requests()` to review existing test patterns in the codebase.

Use `/doc` after testing to update documentation.
