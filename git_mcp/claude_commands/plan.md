---
description: Generate development plan based on issue analysis
argument-hint: [optional context or specific requirements]
allowed-tools: Bash(git *)
---

# 📋 Development Plan Generator

Generate a structured development plan based on the analyzed issue.

**Context:** $ARGUMENTS

## Plan Generation

Create a comprehensive development plan including:

1. **Branch Strategy** - suggest branch name and workflow
2. **File Structure** - what files need to be created/modified
3. **Implementation Steps** - ordered task breakdown
4. **Testing Strategy** - what tests are needed
5. **Documentation Updates** - README, docs, comments

## Repository Context

Analyze current repository structure:

!git branch -a
!git status
!find . -name "*.py" -o -name "*.js" -o -name "*.ts" | head -20

Based on the issue requirements and current codebase, provide a detailed implementation roadmap.

Use `/implement` to start coding based on this plan.
