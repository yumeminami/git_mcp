---
description: Create pull/merge request and close related issue
argument-hint: [issue-id] [optional: target-branch]
allowed-tools: Bash(git *), mcp__git-mcp-server__*
---

# 🚀 Pull Request Creation

Create a pull/merge request and close the related issue.

**Issue ID:** $ARGUMENTS

## PR Creation Process

1. **Prepare Branch**
   !git add .
   !git status
   !git commit -m "Implement feature for issue #$ARGUMENTS"

2. **Push to Remote**
   !git push -u origin HEAD

3. **Create Pull/Merge Request**
   Using our MCP tools to create the PR/MR with:
   - Descriptive title linking to issue
   - Comprehensive description
   - Closes #$ARGUMENTS in description
   - Appropriate labels and reviewers

4. **PR Description Template**
   ```
   ## Summary
   Implements [feature description] as requested in issue #$ARGUMENTS

   ## Changes Made
   - [List of changes]

   ## Testing
   - [Test coverage details]

   ## Documentation
   - [Documentation updates]

   Closes #$ARGUMENTS
   ```

5. **Final Steps**
   - Link PR to original issue
   - Request code review
   - Monitor CI/CD pipeline
   - Address review feedback

**Workflow Complete!** From issue analysis to PR creation.
