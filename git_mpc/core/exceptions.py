"""Custom exceptions for git-mcp."""


class GitMCPError(Exception):
    """Base exception for all git-mcp errors."""

    pass


class ConfigurationError(GitMCPError):
    """Configuration related errors."""

    pass


class AuthenticationError(GitMCPError):
    """Authentication related errors."""

    pass


class PlatformError(GitMCPError):
    """Platform specific errors."""

    def __init__(self, message: str, platform: str, status_code: int = None):
        super().__init__(message)
        self.platform = platform
        self.status_code = status_code


class ResourceNotFoundError(GitMCPError):
    """Resource not found errors."""

    def __init__(self, resource_type: str, resource_id: str, platform: str = None):
        message = f"{resource_type} '{resource_id}' not found"
        if platform:
            message += f" on {platform}"
        super().__init__(message)
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.platform = platform


class PermissionError(GitMCPError):
    """Permission denied errors."""

    pass


class NetworkError(GitMCPError):
    """Network related errors."""

    pass


class ValidationError(GitMCPError):
    """Data validation errors."""

    pass
