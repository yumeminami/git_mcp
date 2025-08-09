#!/bin/bash
# Git MCP Server Installation Script

set -e

echo "🚀 Installing Git MCP Server globally..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Please install uv first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Check if claude command is available
if ! command -v claude &> /dev/null; then
    echo "❌ Claude Code CLI is not installed. Please install Claude Code first."
    exit 1
fi

# Get the current directory (project root)
PROJECT_ROOT=$(pwd)

echo "📦 Installing Git MCP Server as global tool..."
uv tool install --from "$PROJECT_ROOT" git_mcp_server

echo "🔧 Adding to Claude Code (user scope)..."
claude mcp add -s user git-mcp-server git-mcp-server

echo "📋 Installing issue-to-code workflow slash commands..."
# Create user commands directory
USER_COMMANDS_DIR="$HOME/.claude/commands"
mkdir -p "$USER_COMMANDS_DIR"

# Copy slash commands to user directory
cp -r "$PROJECT_ROOT/.claude/commands/"* "$USER_COMMANDS_DIR/"

echo ""
echo "✅ Installation completed successfully!"
echo ""
echo "🎯 Next steps:"
echo "1. Configure a Git platform:"
echo "   git-mcp config add my-gitlab gitlab --url https://gitlab.com"
echo ""
echo "2. Test the connection:"
echo "   git-mcp config test my-gitlab"
echo ""
echo "3. Use the issue-to-code workflow:"
echo "   /issue <issue-url>"
echo "   /plan"
echo "   /implement"
echo "   /test"
echo "   /doc"
echo "   /pr <issue-id>"
echo ""
echo "📚 Available features:"
echo "   - git-mcp          # CLI interface"
echo "   - git-mcp-server   # MCP server"
echo "   - /issue → /pr     # Complete workflow slash commands"
echo ""
echo "🔍 Verify installation:"
echo "   which git-mcp-server"
echo "   claude mcp list"
echo "   ls ~/.claude/commands"
echo ""
echo "🎉 Happy issue-driven coding!"
