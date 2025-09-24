# Codex Integration Slash Commands

This directory contains slash commands for Codex integration with git_mcp_server.

## Installation

These commands are automatically installed to `~/.codex/prompts/` when you run:

```bash
git-mcp-server --install-codex
```

## Available Commands

| Command | Purpose | Usage |
|---------|---------|-------|
| `/issue` | Analyze GitLab/GitHub issues | `/issue <issue-url>` or `/issue` for dashboard |
| `/plan` | Generate development plan | `/plan` (run after `/issue`) |
| `/implement` | Execute implementation | `/implement` (run after `/plan`) |
| `/test` | Run tests and validation | `/test` (run after `/implement`) |
| `/doc` | Update documentation | `/doc` (run after `/test`) |
| `/pr` | Create pull request | `/pr <issue-id>` (run after `/doc`) |

## Workflow

The typical issue-to-code workflow in Codex:

1. **Analyze Issue**: `/issue https://github.com/user/repo/issues/123`
2. **Plan Implementation**: `/plan`
3. **Implement Code**: `/implement`
4. **Run Tests**: `/test`
5. **Update Docs**: `/doc`
6. **Create PR**: `/pr 123`

## MCP Tools

All commands use the `mcp__git-mcp-server__*` tools to interact with Git platforms through the Model Context Protocol.

## Configuration

Requires:
- Codex CLI installed and configured
- `~/.codex/config.toml` with MCP server configuration
- Git platform configured via `git-mcp config add`

## Memory Integration

Code memory guidelines are automatically added to `~/.codex/AGENTS.md` during installation to help Codex understand project patterns and coding standards.
