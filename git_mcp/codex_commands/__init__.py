"""Codex integration slash commands for git_mcp_server.

This module contains slash commands for Codex integration,
providing the issue-to-code workflow for OpenAI Codex users.
"""

__version__ = "1.0.0"
__author__ = "git_mcp_server"

# Available command files
CODEX_COMMANDS = [
    "issue.md",
    "plan.md",
    "implement.md",
    "test.md",
    "doc.md",
    "pr.md",
]
