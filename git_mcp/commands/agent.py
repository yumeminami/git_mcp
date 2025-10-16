"""Agent management commands."""

import asyncio
import json
import sys
from typing import Any, Dict, List, Optional

import click
import yaml
from rich.console import Console
from rich.table import Table

from ..core.context import pass_context
from ..core.exceptions import GitMCPError
from ..services.agent_service import get_agent_service


console = Console()


@click.group()
def agent():
    """Manage external agents and workflows."""
    pass


@agent.command()
@pass_context
async def list(ctx: Any) -> None:
    """List all registered agents."""
    try:
        agent_service = get_agent_service()
        agents = agent_service.list_agents()
        
        if ctx.output_format == "json":
            agent_data = {
                name: agent.model_dump() for name, agent in agents.items()
            }
            click.echo(json.dumps(agent_data, indent=2))
        elif ctx.output_format == "yaml":
            agent_data = {
                name: agent.model_dump() for name, agent in agents.items()
            }
            click.echo(yaml.safe_dump(agent_data, default_flow_style=False))
        else:
            # Table format
            if not agents:
                console.print("No agents registered", style="yellow")
                return
            
            table = Table(title=f"Registered Agents ({len(agents)})")
            table.add_column("Name", style="cyan")
            table.add_column("Description", style="white")
            table.add_column("Version", style="green")
            table.add_column("Author", style="blue")
            table.add_column("Triggers", style="magenta")
            table.add_column("Command", style="dim white")
            
            for name, agent in agents.items():
                triggers = ", ".join(agent.triggers) if agent.triggers else "none"
                author = agent.author or "unknown"
                table.add_row(
                    name,
                    agent.description[:50] + "..." if len(agent.description) > 50 else agent.description,
                    agent.version,
                    author,
                    triggers,
                    agent.command
                )
            
            console.print(table)
            
    except Exception as e:
        console.print(f"Error listing agents: {e}", style="red")
        sys.exit(1)


@agent.command()
@click.argument("agent_name")
@pass_context
async def show(ctx: Any, agent_name: str) -> None:
    """Show detailed information about a specific agent."""
    try:
        agent_service = get_agent_service()
        agent = agent_service.get_agent(agent_name)
        
        if not agent:
            console.print(f"Agent not found: {agent_name}", style="red")
            sys.exit(1)
        
        if ctx.output_format == "json":
            click.echo(json.dumps(agent.model_dump(), indent=2))
        elif ctx.output_format == "yaml":
            click.echo(yaml.safe_dump(agent.model_dump(), default_flow_style=False))
        else:
            # Rich format
            console.print(f"\n[bold cyan]Agent: {agent_name}[/bold cyan]")
            console.print(f"[bold]Description:[/bold] {agent.description}")
            console.print(f"[bold]Version:[/bold] {agent.version}")
            if agent.author:
                console.print(f"[bold]Author:[/bold] {agent.author}")
            console.print(f"[bold]Command:[/bold] {agent.command}")
            if agent.args:
                console.print(f"[bold]Arguments:[/bold] {' '.join(agent.args)}")
            if agent.env:
                console.print(f"[bold]Environment:[/bold]")
                for key, value in agent.env.items():
                    console.print(f"  {key}={value}")
            if agent.triggers:
                console.print(f"[bold]Triggers:[/bold] {', '.join(agent.triggers)}")
            if agent.dependencies:
                console.print(f"[bold]Dependencies:[/bold] {', '.join(agent.dependencies)}")
            console.print(f"[bold]Input Format:[/bold] {agent.input_format}")
            console.print(f"[bold]Output Format:[/bold] {agent.output_format}")
            
            # Check dependencies
            missing_deps = agent_service.validate_agent_dependencies(agent_name)
            if missing_deps:
                console.print(f"\n[bold red]Missing Dependencies:[/bold red] {', '.join(missing_deps)}")
            else:
                console.print("\n[bold green]All dependencies satisfied[/bold green]")
            
    except Exception as e:
        console.print(f"Error showing agent details: {e}", style="red")
        sys.exit(1)


@agent.command()
@click.argument("agent_name")
@click.option("--input", "-i", help="Input data (JSON string)")
@click.option("--input-file", "-f", type=click.File("r"), help="Input data from file")
@click.option("--config", "-c", help="Configuration (JSON string)")
@click.option("--timeout", "-t", default=30.0, help="Execution timeout in seconds")
@pass_context
async def execute(
    ctx: Any,
    agent_name: str,
    input: Optional[str],
    input_file: Optional[click.File],
    config: Optional[str],
    timeout: float
) -> None:
    """Execute an agent with given input and configuration."""
    try:
        agent_service = get_agent_service()
        
        # Parse input data
        input_data = None
        if input:
            input_data = json.loads(input)
        elif input_file:
            input_data = json.load(input_file)
        
        # Parse config
        config_data = None
        if config:
            config_data = json.loads(config)
        
        # Execute agent
        console.print(f"Executing agent: {agent_name}")
        if input_data:
            console.print(f"Input: {json.dumps(input_data, indent=2)}")
        if config_data:
            console.print(f"Config: {json.dumps(config_data, indent=2)}")
        
        result = await agent_service.execute_agent(agent_name, input_data, config_data, timeout)
        
        if ctx.output_format == "json":
            click.echo(json.dumps(result.model_dump(), indent=2))
        elif ctx.output_format == "yaml":
            click.echo(yaml.safe_dump(result.model_dump(), default_flow_style=False))
        else:
            # Rich format
            if result.success:
                console.print(f"\n[bold green]✓ Agent executed successfully[/bold green]")
                console.print(f"[bold]Execution time:[/bold] {result.execution_time:.2f}s")
                if result.output:
                    console.print(f"\n[bold]Output:[/bold]")
                    if isinstance(result.output, (dict, list)):
                        console.print(json.dumps(result.output, indent=2))
                    else:
                        console.print(str(result.output))
            else:
                console.print(f"\n[bold red]✗ Agent execution failed[/bold red]")
                console.print(f"[bold]Error:[/bold] {result.error}")
                console.print(f"[bold]Execution time:[/bold] {result.execution_time:.2f}s")
                sys.exit(1)
                
    except Exception as e:
        console.print(f"Error executing agent: {e}", style="red")
        sys.exit(1)


@agent.command()
@click.argument("repo_url")
@pass_context
async def discover(ctx: Any, repo_url: str) -> None:
    """Discover agents from an external repository."""
    try:
        agent_service = get_agent_service()
        
        console.print(f"Discovering agents from: {repo_url}")
        discovered_agents = await agent_service.discover_agents_from_repo(repo_url)
        
        if ctx.output_format == "json":
            agent_data = [agent.model_dump() for agent in discovered_agents]
            click.echo(json.dumps(agent_data, indent=2))
        elif ctx.output_format == "yaml":
            agent_data = [agent.model_dump() for agent in discovered_agents]
            click.echo(yaml.safe_dump(agent_data, default_flow_style=False))
        else:
            # Table format
            if not discovered_agents:
                console.print("No agents discovered", style="yellow")
                return
            
            table = Table(title=f"Discovered Agents ({len(discovered_agents)})")
            table.add_column("Name", style="cyan")
            table.add_column("Description", style="white")
            table.add_column("Version", style="green")
            table.add_column("Command", style="dim white")
            
            for agent in discovered_agents:
                table.add_row(
                    agent.name,
                    agent.description[:50] + "..." if len(agent.description) > 50 else agent.description,
                    agent.version,
                    agent.command
                )
            
            console.print(table)
            
    except Exception as e:
        console.print(f"Error discovering agents: {e}", style="red")
        sys.exit(1)


@agent.command()
@click.argument("repo_url")
@pass_context
async def add_repo(ctx: Any, repo_url: str) -> None:
    """Add an external agent repository and register discovered agents."""
    try:
        agent_service = get_agent_service()
        
        console.print(f"Adding repository: {repo_url}")
        new_agents = await agent_service.add_external_repository(repo_url)
        
        if ctx.output_format == "json":
            result = {
                "repository": repo_url,
                "new_agents": new_agents,
                "count": len(new_agents)
            }
            click.echo(json.dumps(result, indent=2))
        elif ctx.output_format == "yaml":
            result = {
                "repository": repo_url,
                "new_agents": new_agents,
                "count": len(new_agents)
            }
            click.echo(yaml.safe_dump(result, default_flow_style=False))
        else:
            if new_agents:
                console.print(f"[bold green]✓ Added {len(new_agents)} new agents:[/bold green]")
                for agent_name in new_agents:
                    console.print(f"  • {agent_name}")
            else:
                console.print("No new agents found or all agents already registered", style="yellow")
                
    except Exception as e:
        console.print(f"Error adding repository: {e}", style="red")
        sys.exit(1)


@agent.command()
@click.argument("trigger")
@pass_context
async def by_trigger(ctx: Any, trigger: str) -> None:
    """Find agents by trigger (e.g., 'code_review', 'testing', 'documentation')."""
    try:
        agent_service = get_agent_service()
        matching_agents = agent_service.get_agents_by_trigger(trigger)
        
        if ctx.output_format == "json":
            result = {
                "trigger": trigger,
                "matching_agents": matching_agents,
                "count": len(matching_agents)
            }
            click.echo(json.dumps(result, indent=2))
        elif ctx.output_format == "yaml":
            result = {
                "trigger": trigger,
                "matching_agents": matching_agents,
                "count": len(matching_agents)
            }
            click.echo(yaml.safe_dump(result, default_flow_style=False))
        else:
            if matching_agents:
                console.print(f"[bold cyan]Agents for trigger '{trigger}':[/bold cyan]")
                for agent_name in matching_agents:
                    console.print(f"  • {agent_name}")
            else:
                console.print(f"No agents found for trigger: {trigger}", style="yellow")
                
    except Exception as e:
        console.print(f"Error finding agents by trigger: {e}", style="red")
        sys.exit(1)


@agent.command()
@click.argument("agent_names", nargs=-1, required=True)
@click.option("--input", "-i", help="Initial input data (JSON string)")
@click.option("--input-file", "-f", type=click.File("r"), help="Initial input data from file")
@click.option("--config", "-c", help="Configuration (JSON string)")
@pass_context
async def workflow(
    ctx: Any,
    agent_names: List[str],
    input: Optional[str],
    input_file: Optional[click.File],
    config: Optional[str]
) -> None:
    """Execute a workflow of multiple agents in sequence."""
    try:
        agent_service = get_agent_service()
        
        # Parse input data
        input_data = None
        if input:
            input_data = json.loads(input)
        elif input_file:
            input_data = json.load(input_file)
        
        # Parse config
        config_data = None
        if config:
            config_data = json.loads(config)
        
        # Execute workflow
        console.print(f"Executing workflow: {' → '.join(agent_names)}")
        if input_data:
            console.print(f"Initial input: {json.dumps(input_data, indent=2)}")
        if config_data:
            console.print(f"Config: {json.dumps(config_data, indent=2)}")
        
        results = await agent_service.execute_agent_workflow(agent_names, input_data, config_data)
        
        if ctx.output_format == "json":
            result_data = [result.model_dump() for result in results]
            click.echo(json.dumps(result_data, indent=2))
        elif ctx.output_format == "yaml":
            result_data = [result.model_dump() for result in results]
            click.echo(yaml.safe_dump(result_data, default_flow_style=False))
        else:
            # Rich format
            console.print(f"\n[bold]Workflow Results:[/bold]")
            for i, result in enumerate(results):
                agent_name = result.agent_name
                if result.success:
                    console.print(f"  {i+1}. [green]✓[/green] {agent_name} ({result.execution_time:.2f}s)")
                else:
                    console.print(f"  {i+1}. [red]✗[/red] {agent_name} - {result.error}")
                    break
            
            # Show final output
            if results and results[-1].success:
                console.print(f"\n[bold]Final Output:[/bold]")
                final_output = results[-1].output
                if isinstance(final_output, (dict, list)):
                    console.print(json.dumps(final_output, indent=2))
                else:
                    console.print(str(final_output))
                    
    except Exception as e:
        console.print(f"Error executing workflow: {e}", style="red")
        sys.exit(1)


@agent.command()
@click.argument("name")
@click.argument("description")
@click.argument("command")
@click.option("--args", "-a", multiple=True, help="Command arguments")
@click.option("--triggers", "-t", multiple=True, help="Workflow triggers")
@click.option("--dependencies", "-d", multiple=True, help="Agent dependencies")
@click.option("--input-format", default="json", help="Input format (json, yaml, text)")
@click.option("--output-format", default="json", help="Output format (json, yaml, text)")
@click.option("--version", default="1.0.0", help="Agent version")
@click.option("--author", help="Agent author")
@pass_context
async def register(
    ctx: Any,
    name: str,
    description: str,
    command: str,
    args: List[str],
    triggers: List[str],
    dependencies: List[str],
    input_format: str,
    output_format: str,
    version: str,
    author: Optional[str]
) -> None:
    """Register a custom agent manually."""
    try:
        from ..services.agent_service import AgentDefinition
        
        agent_service = get_agent_service()
        
        agent = AgentDefinition(
            name=name,
            description=description,
            command=command,
            args=list(args),
            triggers=list(triggers),
            dependencies=list(dependencies),
            input_format=input_format,
            output_format=output_format,
            version=version,
            author=author
        )
        
        agent_service.register_agent(agent)
        
        if ctx.output_format == "json":
            result = {"agent_name": name, "success": True}
            click.echo(json.dumps(result, indent=2))
        elif ctx.output_format == "yaml":
            result = {"agent_name": name, "success": True}
            click.echo(yaml.safe_dump(result, default_flow_style=False))
        else:
            console.print(f"[bold green]✓ Agent '{name}' registered successfully[/bold green]")
            
    except Exception as e:
        console.print(f"Error registering agent: {e}", style="red")
        sys.exit(1)


@agent.command()
@click.argument("agent_name")
@pass_context
async def unregister(ctx: Any, agent_name: str) -> None:
    """Unregister an agent."""
    try:
        agent_service = get_agent_service()
        success = agent_service.unregister_agent(agent_name)
        
        if ctx.output_format == "json":
            result = {"agent_name": agent_name, "success": success}
            click.echo(json.dumps(result, indent=2))
        elif ctx.output_format == "yaml":
            result = {"agent_name": agent_name, "success": success}
            click.echo(yaml.safe_dump(result, default_flow_style=False))
        else:
            if success:
                console.print(f"[bold green]✓ Agent '{agent_name}' unregistered successfully[/bold green]")
            else:
                console.print(f"[bold red]✗ Agent '{agent_name}' not found[/bold red]")
                sys.exit(1)
                
    except Exception as e:
        console.print(f"Error unregistering agent: {e}", style="red")
        sys.exit(1)