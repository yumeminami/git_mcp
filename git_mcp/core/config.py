"""Configuration management for git-mcp."""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
import keyring
from pydantic import BaseModel, Field


@dataclass
class PlatformConfig:
    """Configuration for a single Git platform."""

    name: str
    type: str  # 'gitlab', 'github', 'bitbucket'
    url: str
    token: Optional[str] = None
    username: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding sensitive data."""
        data = asdict(self)
        # Remove token from config file, it's stored in keyring
        data.pop("token", None)
        return data


class DefaultSettings(BaseModel):
    """Default settings for git-mcp."""

    platform: str = "gitlab"
    output_format: str = Field(default="table", pattern="^(table|json|yaml)$")
    page_size: int = Field(default=20, gt=0, le=100)
    timeout: int = Field(default=30, gt=0)


class Alias(BaseModel):
    """Alias configuration."""

    name: str
    platform: str
    project: Optional[str] = None
    description: Optional[str] = None


class GitMCPConfig:
    """Main configuration manager for git-mcp."""

    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = config_dir or Path.home() / ".git-mcp"
        self.config_file = self.config_dir / "config.yaml"
        self.platforms: Dict[str, PlatformConfig] = {}
        self.defaults = DefaultSettings()
        self.aliases: List[Alias] = []

        # Ensure config directory exists
        self.config_dir.mkdir(exist_ok=True)

        # Load existing configuration
        self.load()

    def load(self) -> None:
        """Load configuration from file."""
        if not self.config_file.exists():
            return

        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}

            # Load platforms
            platforms_data = data.get("platforms", {})
            for name, platform_data in platforms_data.items():
                # Make a copy to avoid modifying the original data
                platform_data_copy = platform_data.copy()
                # Remove 'name' if it exists to avoid conflict
                platform_data_copy.pop("name", None)
                platform_config = PlatformConfig(name=name, **platform_data_copy)
                # Load token from keyring
                platform_config.token = self.get_token(name)
                self.platforms[name] = platform_config

            # Load defaults
            defaults_data = data.get("defaults", {})
            self.defaults = DefaultSettings(**defaults_data)

            # Load aliases
            aliases_data = data.get("aliases", [])
            self.aliases = [Alias(**alias) for alias in aliases_data]

        except Exception as e:
            raise ValueError(f"Failed to load configuration: {e}")

    def save(self) -> None:
        """Save configuration to file."""
        data = {
            "platforms": {
                name: config.to_dict() for name, config in self.platforms.items()
            },
            "defaults": self.defaults.model_dump(),
            "aliases": [alias.model_dump() for alias in self.aliases],
        }

        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                yaml.dump(data, f, default_flow_style=False, indent=2)
        except Exception as e:
            raise ValueError(f"Failed to save configuration: {e}")

    async def add_platform(
        self,
        name: str,
        platform_type: str,
        url: str,
        token: Optional[str] = None,
        username: Optional[str] = None,
        auto_fetch_username: bool = True,
    ) -> None:
        """Add a new platform configuration.

        Args:
            name: Platform name
            platform_type: Platform type ('gitlab', 'github', etc.)
            url: Platform URL
            token: Access token
            username: Username (if not provided and token is given, will try to fetch automatically)
            auto_fetch_username: Whether to automatically fetch username from token
        """
        # If username not provided and token is available, try to fetch it automatically
        if auto_fetch_username and token and not username:
            try:
                username = await self._fetch_username_from_token(
                    platform_type, url, token
                )
            except Exception as e:
                print(f"Warning: Could not fetch username automatically: {e}")

        platform_config = PlatformConfig(
            name=name, type=platform_type, url=url, token=token, username=username
        )

        self.platforms[name] = platform_config

        # Save token to keyring if provided
        if token:
            self.set_token(name, token)

        self.save()

    def remove_platform(self, name: str) -> None:
        """Remove a platform configuration."""
        if name in self.platforms:
            # Remove token from keyring
            self.remove_token(name)
            del self.platforms[name]
            self.save()
        else:
            raise ValueError(f"Platform '{name}' not found")

    def get_platform(self, name: str) -> Optional[PlatformConfig]:
        """Get platform configuration by name."""
        return self.platforms.get(name)

    def list_platforms(self) -> List[str]:
        """List all configured platform names."""
        return list(self.platforms.keys())

    def set_token(self, platform_name: str, token: str) -> None:
        """Store token securely in keyring."""
        keyring.set_password("git-mcp", platform_name, token)
        if platform_name in self.platforms:
            self.platforms[platform_name].token = token

    def get_token(self, platform_name: str) -> Optional[str]:
        """Retrieve token from keyring or environment variable.

        For SSH sessions where keychain is inaccessible, falls back to:
        - GIT_MCP_{PLATFORM_NAME}_TOKEN environment variable
        - GIT_MCP_TOKEN_{PLATFORM_NAME} environment variable (alternative format)
        """
        import os

        # Try environment variables first (useful for SSH sessions)
        env_token = os.environ.get(
            f"GIT_MCP_{platform_name.upper()}_TOKEN"
        ) or os.environ.get(f"GIT_MCP_TOKEN_{platform_name.upper()}")
        if env_token:
            return env_token

        # Fall back to keyring
        try:
            return keyring.get_password("git-mcp", platform_name)
        except (keyring.errors.KeyringError, Exception):
            # If keyring fails (common in SSH sessions), check env vars again with error message
            if not env_token:
                import sys

                print(
                    f"Warning: Cannot access keychain (SSH session?). Set GIT_MCP_{platform_name.upper()}_TOKEN environment variable.",
                    file=sys.stderr,
                )
            return None

    def remove_token(self, platform_name: str) -> None:
        """Remove token from keyring."""
        try:
            keyring.delete_password("git-mcp", platform_name)
        except keyring.errors.PasswordDeleteError:
            pass  # Token didn't exist

    def add_alias(
        self,
        name: str,
        platform: str,
        project: Optional[str] = None,
        description: Optional[str] = None,
    ) -> None:
        """Add a new alias."""
        alias = Alias(
            name=name, platform=platform, project=project, description=description
        )
        # Remove existing alias with same name
        self.aliases = [a for a in self.aliases if a.name != name]
        self.aliases.append(alias)
        self.save()

    def remove_alias(self, name: str) -> None:
        """Remove an alias."""
        self.aliases = [a for a in self.aliases if a.name != name]
        self.save()

    def get_alias(self, name: str) -> Optional[Alias]:
        """Get alias by name."""
        for alias in self.aliases:
            if alias.name == name:
                return alias
        return None

    async def _fetch_username_from_token(
        self, platform_type: str, url: str, token: str
    ) -> Optional[str]:
        """Fetch username from platform using token."""
        try:
            if platform_type.lower() == "gitlab":
                from ..platforms.gitlab import GitLabAdapter

                gitlab_adapter = GitLabAdapter(url, token)
                user_info = await gitlab_adapter.get_current_user()
                return user_info.get("username")
            elif platform_type.lower() == "github":
                from ..platforms.github import GitHubAdapter

                github_adapter = GitHubAdapter(url, token)
                user_info = await github_adapter.get_current_user()
                return user_info.get("username")
            else:
                print(
                    f"Warning: Username auto-fetch not supported for platform type: {platform_type}"
                )
                return None
        except Exception as e:
            raise Exception(f"Failed to fetch username from {platform_type}: {e}")

    async def refresh_username(self, platform_name: str) -> bool:
        """Refresh username for an existing platform configuration.

        Returns:
            bool: True if username was successfully updated, False otherwise
        """
        platform_config = self.platforms.get(platform_name)
        if not platform_config:
            raise ValueError(f"Platform '{platform_name}' not found")

        if not platform_config.token:
            raise ValueError(f"No token available for platform '{platform_name}'")

        try:
            username = await self._fetch_username_from_token(
                platform_config.type, platform_config.url, platform_config.token
            )
            if username:
                platform_config.username = username
                self.save()
                return True
            return False
        except Exception as e:
            raise Exception(f"Failed to refresh username for {platform_name}: {e}")

    def update_defaults(self, **kwargs) -> None:
        """Update default settings."""
        current_dict = self.defaults.model_dump()
        current_dict.update(kwargs)
        self.defaults = DefaultSettings(**current_dict)
        self.save()


# Global configuration instance
_config_instance: Optional[GitMCPConfig] = None


def get_config() -> GitMCPConfig:
    """Get the global configuration instance."""
    global _config_instance
    if _config_instance is None:
        _config_instance = GitMCPConfig()
    return _config_instance


def init_config(config_dir: Optional[Path] = None) -> GitMCPConfig:
    """Initialize configuration with custom directory."""
    global _config_instance
    _config_instance = GitMCPConfig(config_dir)
    return _config_instance
