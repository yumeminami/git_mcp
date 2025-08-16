"""Git MCP Server (git-mcp)

A unified command-line tool for managing Git repositories across GitHub and GitLab platforms.
"""

import importlib.metadata

try:
    __version__ = importlib.metadata.version("git_mcp_server")
except importlib.metadata.PackageNotFoundError:
    # Fallback for development/source installations
    __version__ = "0.2.0"

__author__ = "Git MCP Team"


def get_version() -> str:
    """Get the package version dynamically."""
    return __version__
