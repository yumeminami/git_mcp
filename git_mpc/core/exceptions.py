"""Custom exceptions for git-mpc."""


class GitMPCError(Exception):
    """Base exception for all git-mpc errors."""

    pass


class ConfigurationError(GitMPCError):
    """Configuration related errors."""

    pass


class AuthenticationError(GitMPCError):
    """Authentication related errors."""

    pass


class PlatformError(GitMPCError):
    """Platform specific errors."""

    def __init__(self, message: str, platform: str, status_code: int = None):
        super().__init__(message)
        self.platform = platform
        self.status_code = status_code


class ResourceNotFoundError(GitMPCError):
    """Resource not found errors."""

    def __init__(self, resource_type: str, resource_id: str, platform: str = None):
        message = f"{resource_type} '{resource_id}' not found"
        if platform:
            message += f" on {platform}"
        super().__init__(message)
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.platform = platform


class PermissionError(GitMPCError):
    """Permission denied errors."""

    pass


class NetworkError(GitMPCError):
    """Network related errors."""

    pass


class ValidationError(GitMPCError):
    """Data validation errors."""

    pass
