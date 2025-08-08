---
description: Generate comprehensive tests for implemented functionality
argument-hint: [specific component or test type]
allowed-tools: Read, Write, Edit, Bash(pytest *), Bash(npm test *)
---

# 🧪 Test Generation

Generate comprehensive tests for the implemented functionality.

**Test Focus:** $ARGUMENTS

## Test Strategy

1. **Analyze Implementation**
   - Review the implemented code
   - Identify testable components
   - Determine test coverage requirements

2. **Generate Test Cases**
   - Unit tests for core functionality
   - Integration tests for component interaction
   - Edge cases and error handling
   - Mock external dependencies if needed

3. **Test Types to Create**
   - Happy path scenarios
   - Error conditions and exceptions
   - Boundary value testing
   - Performance tests (if applicable)

## Test Execution

Run tests to ensure they pass:
!pytest tests/ -v
# or
!npm test

Aim for high test coverage and meaningful assertions.

Use `/doc` after testing to update documentation.
