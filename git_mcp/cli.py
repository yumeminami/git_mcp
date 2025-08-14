"""Command-line interface for git-mcp."""

import asyncio
import click

from .commands.project import project_commands
from .commands.issue import issue_commands
from .commands.mr import mr_commands
from .core.config import get_config
from .core.exceptions import GitMCPError
from .core.logging import setup_logging, get_logger
from .utils.output import OutputFormatter
from . import get_version


# Global context for CLI
class CLIContext:
    def __init__(self):
        self.config = get_config()
        self.output_format = "table"
        self.platform = None
        self.formatter = None
        self.debug = False
        self.logger = None

    def get_formatter(self) -> OutputFormatter:
        if not self.formatter:
            self.formatter = OutputFormatter(self.output_format)
        return self.formatter

    def get_logger(self):
        if not self.logger:
            self.logger = get_logger("git_mcp.cli")
        return self.logger


@click.group(invoke_without_command=True)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["table", "json", "yaml"]),
    default=None,
    help="Output format",
)
@click.option("--platform", help="Default platform to use")
@click.option("--config-dir", type=click.Path(), help="Configuration directory path")
@click.option("--debug", is_flag=True, help="Enable debug logging")
@click.option(
    "--version",
    is_flag=True,
    help="Show version and exit",
)
@click.pass_context
def cli(ctx, output_format, platform, config_dir, debug, version):
    """Git MCP Server - Unified management for GitHub and GitLab."""
    if version:
        click.echo(f"git-mcp {get_version()}")
        ctx.exit()

    # If no subcommand is provided, show help
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
        ctx.exit()

    ctx.ensure_object(CLIContext)

    # Setup logging first
    if debug:
        setup_logging(debug=True)
        ctx.obj.debug = True
        logger = ctx.obj.get_logger()
        logger.debug("Debug logging enabled")

    if config_dir:
        from pathlib import Path
        from .core.config import init_config

        if ctx.obj.debug:
            logger = ctx.obj.get_logger()
            logger.debug(f"Using custom config directory: {config_dir}")

        init_config(Path(config_dir))
        ctx.obj.config = get_config()

    if output_format:
        ctx.obj.output_format = output_format
    else:
        ctx.obj.output_format = ctx.obj.config.defaults.output_format

    if platform:
        ctx.obj.platform = platform
    else:
        ctx.obj.platform = ctx.obj.config.defaults.platform

    if ctx.obj.debug:
        logger = ctx.obj.get_logger()
        logger.debug(f"Output format: {ctx.obj.output_format}")
        logger.debug(f"Default platform: {ctx.obj.platform}")
        logger.debug(f"Config loaded from: {ctx.obj.config.config_dir}")


@cli.group()
def config():
    """Manage git-mcp configuration."""
    pass


@config.command("add")
@click.argument("name")
@click.argument("type", type=click.Choice(["gitlab", "github"]))
@click.option("--url", required=True, help="Platform URL")
@click.option("--token", prompt=True, hide_input=True, help="Access token")
@click.option("--username", help="Username (optional, will auto-fetch if not provided)")
@click.option(
    "--no-auto-username", is_flag=True, help="Disable automatic username fetching"
)
@click.pass_context
def config_add(ctx, name, type, url, token, username, no_auto_username):
    """Add a new platform configuration.

    After successful configuration, you'll be prompted to set up environment
    variables for SSH sessions or CI/CD environments where keychain access
    may not be available.

    Environment variables take precedence over keychain storage and use the
    format: GIT_MCP_{PLATFORM_NAME}_TOKEN
    """

    async def add_platform():
        try:
            await ctx.obj.config.add_platform(
                name,
                type,
                url,
                token,
                username,
                auto_fetch_username=not no_auto_username,
            )
            formatter = ctx.obj.get_formatter()
            platform_config = ctx.obj.config.get_platform(name)
            if platform_config and platform_config.username:
                formatter.print_success(
                    f"Platform '{name}' added successfully with username '{platform_config.username}'"
                )
            else:
                formatter.print_success(f"Platform '{name}' added successfully")

            # Prompt for environment variable setup
            formatter.print_info(
                "\n💡 For SSH sessions or CI/CD environments, you can also use environment variables:"
            )
            formatter.print_info(
                f"   export GIT_MCP_{name.upper()}_TOKEN='your-token-here'"
            )

            if click.confirm(
                "\nWould you like to see how to set this as an environment variable?"
            ):
                import os

                shell = os.environ.get("SHELL", "/bin/bash").split("/")[-1]

                formatter.print_info("\n📝 To set the environment variable:")
                formatter.print_info("\n1. For current session:")
                formatter.print_info(
                    f"   export GIT_MCP_{name.upper()}_TOKEN='{token}'"
                )

                formatter.print_info(
                    "\n2. To make it permanent, add to your shell config:"
                )
                if shell == "zsh":
                    formatter.print_info(
                        f"   echo 'export GIT_MCP_{name.upper()}_TOKEN=\"your-token\"' >> ~/.zshrc"
                    )
                elif shell == "bash":
                    formatter.print_info(
                        f"   echo 'export GIT_MCP_{name.upper()}_TOKEN=\"your-token\"' >> ~/.bashrc"
                    )
                else:
                    formatter.print_info(
                        f'   Add to your shell config file: export GIT_MCP_{name.upper()}_TOKEN="your-token"'
                    )

                formatter.print_info("\n3. Then reload your shell config:")
                if shell == "zsh":
                    formatter.print_info("   source ~/.zshrc")
                elif shell == "bash":
                    formatter.print_info("   source ~/.bashrc")

                formatter.print_info(
                    "\n⚠️  Note: When using environment variables, they take precedence over keychain storage."
                )
        except Exception as e:
            formatter = ctx.obj.get_formatter()
            formatter.print_error(f"Failed to add platform: {e}")
            ctx.exit(1)

    asyncio.run(add_platform())


@config.command("list")
@click.pass_context
def config_list(ctx):
    """List configured platforms."""
    platforms = ctx.obj.config.list_platforms()
    formatter = ctx.obj.get_formatter()

    if not platforms:
        formatter.print_info("No platforms configured")
        return

    if ctx.obj.output_format == "json":
        import json

        data = []
        for name in platforms:
            platform_config = ctx.obj.config.get_platform(name)
            data.append(
                {
                    "name": name,
                    "type": platform_config.type,
                    "url": platform_config.url,
                    "username": platform_config.username,
                }
            )
        click.echo(json.dumps(data, indent=2))
    else:
        from rich.table import Table

        table = Table(title="Configured Platforms")
        table.add_column("Name")
        table.add_column("Type")
        table.add_column("URL")
        table.add_column("Username")

        for name in platforms:
            platform_config = ctx.obj.config.get_platform(name)
            table.add_row(
                name,
                platform_config.type,
                platform_config.url,
                platform_config.username or "",
            )

        formatter.console.print(table)


@config.command("remove")
@click.argument("name")
@click.confirmation_option(prompt="Are you sure you want to remove this platform?")
@click.pass_context
def config_remove(ctx, name):
    """Remove a platform configuration."""
    try:
        ctx.obj.config.remove_platform(name)
        formatter = ctx.obj.get_formatter()
        formatter.print_success(f"Platform '{name}' removed successfully")
    except GitMCPError as e:
        formatter = ctx.obj.get_formatter()
        formatter.print_error(str(e))
        ctx.exit(1)


@config.command("test")
@click.argument("name", required=False)
@click.pass_context
def config_test(ctx, name):
    """Test platform connection."""

    async def test_platform(platform_name):
        platform_config = ctx.obj.config.get_platform(platform_name)
        if not platform_config:
            raise ValueError(f"Platform '{platform_name}' not found")

        # Import adapter based on type
        if platform_config.type == "gitlab":
            from .platforms.gitlab import GitLabAdapter

            adapter = GitLabAdapter(platform_config.url, platform_config.token)
        elif platform_config.type == "github":
            from .platforms.github import GitHubAdapter

            adapter = GitHubAdapter(platform_config.url, platform_config.token)
        else:
            raise ValueError(
                f"Platform type '{platform_config.type}' not supported yet"
            )

        try:
            success = await adapter.test_connection()
            return success, None
        except Exception as e:
            return False, str(e)

    formatter = ctx.obj.get_formatter()

    if name:
        platforms_to_test = [name]
    else:
        platforms_to_test = ctx.obj.config.list_platforms()

    if not platforms_to_test:
        formatter.print_info("No platforms to test")
        return

    for platform_name in platforms_to_test:
        try:
            success, error = asyncio.run(test_platform(platform_name))
            if success:
                formatter.print_success(f"Connection to '{platform_name}' successful")
            else:
                formatter.print_error(
                    f"Connection to '{platform_name}' failed: {error}"
                )
        except Exception as e:
            formatter.print_error(f"Error testing '{platform_name}': {e}")


@config.command("refresh-username")
@click.argument("name")
@click.pass_context
def config_refresh_username(ctx, name):
    """Refresh username for a platform configuration."""

    async def refresh_username():
        try:
            success = await ctx.obj.config.refresh_username(name)
            formatter = ctx.obj.get_formatter()
            if success:
                platform_config = ctx.obj.config.get_platform(name)
                username = platform_config.username if platform_config else "Unknown"
                formatter.print_success(
                    f"Username for platform '{name}' updated to '{username}'"
                )
            else:
                formatter.print_warning(
                    f"Could not fetch username for platform '{name}'"
                )
        except Exception as e:
            formatter = ctx.obj.get_formatter()
            formatter.print_error(f"Failed to refresh username: {e}")
            ctx.exit(1)

    asyncio.run(refresh_username())


@cli.group()
def project():
    """Manage projects."""
    pass


# Add project commands
for cmd in project_commands:
    project.add_command(cmd)


@cli.group()
def issue():
    """Manage issues."""
    pass


# Add issue commands
for cmd in issue_commands:
    issue.add_command(cmd)


@cli.group()
def mr():
    """Manage merge requests."""
    pass


# Add MR commands
for cmd in mr_commands:
    mr.add_command(cmd)


def main():
    """Main entry point for the CLI."""
    try:
        cli()
    except GitMCPError as e:
        click.echo(f"Error: {e}", err=True)
        exit(1)
    except KeyboardInterrupt:
        click.echo("\nOperation cancelled.", err=True)
        exit(1)


if __name__ == "__main__":
    main()
