---
description: Create pull/merge request and close related issue
argument-hint: [issue-id] [optional: target-branch]
allowed-tools: Bash(git *), mcp__git-mcp-server__*
---

# 🚀 Pull Request Creation

Think about the changes made and how to present them clearly before creating a pull/merge request and closing the related issue.

**Issue ID:** $ARGUMENTS

## PR Creation Process

1. **Prepare Branch**
   !git add .
   !git status
   !git commit -m "Implement feature for issue #$ARGUMENTS"

2. **Push to Remote**
   !git push -u origin HEAD

3. **Create Pull/Merge Request**
   Use `create_merge_request()` to create the PR/MR with:
   - Think about a descriptive title linking to issue
   - Think more about comprehensive description that explains the solution
   - Closes #$ARGUMENTS in description
   - Consider appropriate labels and reviewers

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
   - Link PR to original issue (use `update_issue()` to close issue if needed)
   - Request code review via `get_merge_request_details()` for tracking
   - Monitor CI/CD pipeline
   - Address review feedback

**Workflow Complete!** From issue analysis to PR creation.
