---
description: Generate development plan based on issue analysis using git_mcp_server tools
argument-hint: [optional context or specific requirements]
allowed-tools: Bash(git *), mcp__git-mcp-server__*
---

# 📋 Development Plan Generator

Consider multiple architectural approaches and evaluate their tradeoffs deeply before generating a structured development plan.

**Context:** $ARGUMENTS

## Issue Documentation Update

**First, update issue documentation:**

1. **Find Issue Document** - Look for `.claude/issue-*.md` files in current project
   - If multiple exist, prompt user to specify which issue this plan is for
   - If none exist, suggest running `/issue <issue-url>` first for proper documentation

2. **Update Plan Section** in the issue document:
   - Replace/append to `## 📋 Development Plan (Updated: <timestamp>)` section
   - Include full plan details with timestamp
   - Preserve other sections (analysis, implementation, testing, etc.)

## Plan Generation

Create a comprehensive development plan including:

1. **Branch Strategy** - determine optimal branch name and workflow approach
2. **File Structure** - analyze what files need to be created/modified and their relationships
3. **Implementation Steps** - provide ordered task breakdown with clear dependencies
4. **Testing Strategy** - design comprehensive test coverage plan
5. **Documentation Updates** - identify README, docs, and comment requirements

Use `get_project_details()` to understand project structure and `list_merge_requests()` to review existing workflow patterns.

## Repository Context

Analyze current repository structure:

!git branch -a
!git status
!find . -name "*.py" -o -name "*.js" -o -name "*.ts" | head -20

Based on the issue requirements and current codebase, thoroughly evaluate potential approaches and provide a detailed implementation roadmap with clear rationale for the chosen approach.

**After generating the plan, save it to the issue documentation file.**

Use `/implement` to start coding based on this plan.
