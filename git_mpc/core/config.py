"""Configuration management for git-mpc."""

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
    """Default settings for git-mpc."""

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


class GitMPCConfig:
    """Main configuration manager for git-mpc."""

    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = config_dir or Path.home() / ".git-mpc"
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

    def add_platform(
        self,
        name: str,
        platform_type: str,
        url: str,
        token: Optional[str] = None,
        username: Optional[str] = None,
    ) -> None:
        """Add a new platform configuration."""
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
        keyring.set_password("git-mpc", platform_name, token)
        if platform_name in self.platforms:
            self.platforms[platform_name].token = token

    def get_token(self, platform_name: str) -> Optional[str]:
        """Retrieve token from keyring."""
        return keyring.get_password("git-mpc", platform_name)

    def remove_token(self, platform_name: str) -> None:
        """Remove token from keyring."""
        try:
            keyring.delete_password("git-mpc", platform_name)
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

    def update_defaults(self, **kwargs) -> None:
        """Update default settings."""
        current_dict = self.defaults.model_dump()
        current_dict.update(kwargs)
        self.defaults = DefaultSettings(**current_dict)
        self.save()


# Global configuration instance
_config_instance: Optional[GitMPCConfig] = None


def get_config() -> GitMPCConfig:
    """Get the global configuration instance."""
    global _config_instance
    if _config_instance is None:
        _config_instance = GitMPCConfig()
    return _config_instance


def init_config(config_dir: Optional[Path] = None) -> GitMPCConfig:
    """Initialize configuration with custom directory."""
    global _config_instance
    _config_instance = GitMPCConfig(config_dir)
    return _config_instance
