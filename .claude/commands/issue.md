---
description: Fetch and analyze GitLab/GitHub issue
argument-hint: [issue-url] or [platform] [project-id] [issue-id] (empty to list my issues)
---

# 🎯 Issue Analysis

**Arguments:** $ARGUMENTS

## Mode Selection

If no arguments provided, show **My Issues Dashboard**:
- List issues assigned to me across configured platforms
- Show priority, status, and project context
- Allow selection for detailed analysis

If arguments provided, analyze **Specific Issue**:
- Fetch issue details from URL or platform/project/issue-id
- Provide technical analysis and requirements
- Generate implementation suggestions

## Analysis Output

**For My Issues List:**
1. **Assigned Issues** - issues assigned to current user
2. **Recent Activity** - recently updated issues
3. **Priority Issues** - high priority or urgent items
4. **Selection Prompt** - choose issue for detailed analysis

**For Specific Issue:**
1. **Issue Overview** - title, description, labels, priority
2. **Technical Requirements** - what needs to be implemented
3. **Context Analysis** - review current codebase for related components
4. **Next Steps** - suggested approach for development

Use `/plan` after issue analysis to generate the development plan.
