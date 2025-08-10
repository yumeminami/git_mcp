---
description: Generate development plan based on issue analysis using git_mcp_server tools
argument-hint: [optional context or specific requirements]
allowed-tools: Bash(git *), mcp__git-mcp-server__*
---

# 📋 Development Plan Generator

Think harder about the architecture and approach before generating a structured development plan based on the analyzed issue.

**Context:** $ARGUMENTS

## Plan Generation

Create a comprehensive development plan including:

1. **Branch Strategy** - think about branch name and workflow approach
2. **File Structure** - think more about what files need to be created/modified and their relationships
3. **Implementation Steps** - think through ordered task breakdown with dependencies
4. **Testing Strategy** - think harder about what tests are needed and test coverage
5. **Documentation Updates** - consider README, docs, and comment requirements

Use `get_project_details()` to understand project structure and `list_merge_requests()` to review existing workflow patterns.

## Repository Context

Analyze current repository structure:

!git branch -a
!git status
!find . -name "*.py" -o -name "*.js" -o -name "*.ts" | head -20

Based on the issue requirements and current codebase, think longer about potential approaches and provide a detailed implementation roadmap with rationale for chosen approach.

Use `/implement` to start coding based on this plan.
