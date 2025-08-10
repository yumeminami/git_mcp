---
description: Generate comprehensive test suites using git_mcp_server tools for project context
argument-hint: [optional test type or component focus]
allowed-tools: mcp__git-mcp-server__*
---

# 🧪 Test Generation

Show your complete reasoning when designing comprehensive test suites, considering multiple testing approaches and potential failure scenarios.

**Focus:** $ARGUMENTS

## Issue Documentation Update

**First, update issue documentation:**

1. **Find Issue Document** - Look for `.claude/issue-*.md` files in current project
   - Review implementation progress to understand what needs testing
   - If no issue doc exists, suggest running `/issue`, `/plan`, `/implement` first

2. **Update Testing Section** in the issue document:
   - Update `## 🧪 Testing Status (Updated: <timestamp>)` section
   - Document test strategy and approach
   - Record test files created and test coverage achieved
   - Note any testing challenges or edge cases discovered
   - Track testing completion status

## Test Strategy

1. **Unit Tests** - design thorough testing for individual functions and methods
2. **Integration Tests** - analyze component interactions and dependencies
3. **Edge Cases** - identify boundary conditions and error scenarios
4. **Mock External Dependencies** - isolate components for testing
5. **Test Coverage** - ensure comprehensive coverage across all code paths

## Test Types

- **Happy Path Tests** - normal operation scenarios
- **Error Handling Tests** - exception and error conditions
- **Boundary Tests** - edge cases and limits
- **Integration Tests** - component interactions
- **Performance Tests** - if applicable

Use `get_project_details()` to understand testing frameworks and `list_merge_requests()` to review existing test patterns in the codebase.

**After testing, update the issue documentation with test results and coverage details.**

Use `/doc` after testing to update documentation.
