---
description: Create pull/merge request and close related issue
argument-hint: [issue-id] [optional: target-branch]
allowed-tools: Bash(git *), mcp__git-mcp-server__*
---

# 🚀 Pull Request Creation

Analyze the changes made thoroughly and consider multiple ways to present them clearly and effectively in the pull/merge request.

**Issue ID:** $ARGUMENTS

## Issue Documentation Finalization

**First, finalize issue documentation:**

1. **Find Issue Document** - Look for `.claude/issue-$ARGUMENTS-*.md` in current project
   - Use the provided issue ID to find the correct documentation file
   - If no issue doc exists, create a summary from available git history

2. **Final Update** to the issue document:
   - Update `## 🚀 Pull Request (Updated: <timestamp>)` section
   - Include PR/MR URL, title, and description
   - Summarize all work completed (analysis → plan → implementation → testing → docs → PR)
   - Mark issue as completed
   - Archive or mark for cleanup

## PR Creation Process

1. **Prepare Branch**
   !git add .
   !git status
   !git commit -m "Implement feature for issue #$ARGUMENTS"

2. **Push to Remote**
   !git push -u origin HEAD

3. **Create Pull/Merge Request**
   Use `create_merge_request()` to create the PR/MR with:
   - Craft a descriptive title linking to issue
   - Create comprehensive description that clearly explains the solution
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

6. **Complete Issue Documentation**
   - Save final PR details to `.claude/issue-$ARGUMENTS-*.md`
   - Mark workflow as completed in the documentation
   - Issue document now serves as complete project history for this feature

**Workflow Complete!** From issue analysis to PR creation with full documentation trail.
