"""
Agent Service for managing external agents and workflow orchestration.

This service provides:
1. Agent discovery and registration
2. Agent execution and orchestration
3. Integration with external agent repositories
4. Unified agent configuration management
"""

import asyncio
import json
import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import httpx
import yaml
from pydantic import BaseModel, Field

from ..core.exceptions import GitMCPError

logger = logging.getLogger(__name__)


class AgentDefinition(BaseModel):
    """Definition of an external agent."""
    
    name: str = Field(..., description="Agent name")
    description: str = Field(..., description="Agent description")
    version: str = Field(default="1.0.0", description="Agent version")
    author: Optional[str] = Field(None, description="Agent author")
    
    # Execution configuration
    command: str = Field(..., description="Command to execute agent")
    args: List[str] = Field(default_factory=list, description="Default arguments")
    env: Dict[str, str] = Field(default_factory=dict, description="Environment variables")
    
    # Input/output configuration
    input_format: str = Field(default="json", description="Input format (json, yaml, text)")
    output_format: str = Field(default="json", description="Output format (json, yaml, text)")
    
    # Workflow integration
    triggers: List[str] = Field(default_factory=list, description="Workflow triggers")
    dependencies: List[str] = Field(default_factory=list, description="Agent dependencies")
    
    # Configuration
    config_schema: Optional[Dict[str, Any]] = Field(None, description="Configuration schema")
    default_config: Dict[str, Any] = Field(default_factory=dict, description="Default configuration")


class AgentResult(BaseModel):
    """Result from agent execution."""
    
    agent_name: str
    success: bool
    output: Any
    error: Optional[str] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentService:
    """Service for managing external agents."""
    
    def __init__(self):
        self.config_dir = Path.home() / ".git-mcp" / "agents"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.agents_file = self.config_dir / "agents.yaml"
        self.external_repos_file = self.config_dir / "external_repos.yaml"
        
        self._agents: Dict[str, AgentDefinition] = {}
        self._external_repos: List[str] = []
        
        self._load_configuration()
    
    def _load_configuration(self) -> None:
        """Load agent configuration from files."""
        try:
            # Load registered agents
            if self.agents_file.exists():
                with open(self.agents_file, 'r') as f:
                    agents_data = yaml.safe_load(f) or {}
                    for name, data in agents_data.get('agents', {}).items():
                        self._agents[name] = AgentDefinition(name=name, **data)
            
            # Load external repositories
            if self.external_repos_file.exists():
                with open(self.external_repos_file, 'r') as f:
                    repos_data = yaml.safe_load(f) or {}
                    self._external_repos = repos_data.get('repositories', [])
                    
            logger.info(f"Loaded {len(self._agents)} agents and {len(self._external_repos)} external repos")
            
        except Exception as e:
            logger.warning(f"Failed to load agent configuration: {e}")
    
    def _save_configuration(self) -> None:
        """Save agent configuration to files."""
        try:
            # Save agents
            agents_data = {
                'agents': {
                    name: agent.model_dump(exclude={'name'})
                    for name, agent in self._agents.items()
                }
            }
            with open(self.agents_file, 'w') as f:
                yaml.safe_dump(agents_data, f, default_flow_style=False, sort_keys=True)
            
            # Save external repositories
            repos_data = {'repositories': self._external_repos}
            with open(self.external_repos_file, 'w') as f:
                yaml.safe_dump(repos_data, f, default_flow_style=False)
                
        except Exception as e:
            logger.error(f"Failed to save agent configuration: {e}")
            raise GitMCPError(f"Failed to save agent configuration: {e}")
    
    async def discover_agents_from_repo(self, repo_url: str) -> List[AgentDefinition]:
        """Discover agents from an external repository."""
        discovered_agents = []
        
        try:
            # Clone or fetch repository temporarily
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Clone repository
                process = await asyncio.create_subprocess_exec(
                    'git', 'clone', '--depth', '1', repo_url, str(temp_path / 'repo'),
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                await process.communicate()
                
                if process.returncode != 0:
                    raise GitMCPError(f"Failed to clone repository: {repo_url}")
                
                repo_path = temp_path / 'repo'
                
                # Look for agent definitions
                agent_files = []
                for pattern in ['*.yaml', '*.yml', '*.json']:
                    agent_files.extend(repo_path.rglob(pattern))
                
                for agent_file in agent_files:
                    try:
                        if agent_file.suffix in ['.yaml', '.yml']:
                            with open(agent_file, 'r') as f:
                                data = yaml.safe_load(f)
                        else:
                            with open(agent_file, 'r') as f:
                                data = json.load(f)
                        
                        # Check if it's an agent definition
                        if isinstance(data, dict) and 'name' in data and 'command' in data:
                            agent = AgentDefinition(**data)
                            discovered_agents.append(agent)
                            
                    except Exception as e:
                        logger.debug(f"Skipping file {agent_file}: {e}")
                        continue
                        
        except Exception as e:
            logger.error(f"Failed to discover agents from {repo_url}: {e}")
            raise GitMCPError(f"Failed to discover agents from repository: {e}")
        
        return discovered_agents
    
    async def add_external_repository(self, repo_url: str) -> List[str]:
        """Add an external agent repository and discover agents."""
        if repo_url in self._external_repos:
            return []
        
        # Discover agents from repository
        discovered_agents = await self.discover_agents_from_repo(repo_url)
        
        # Add repository to list
        self._external_repos.append(repo_url)
        
        # Register discovered agents
        new_agents = []
        for agent in discovered_agents:
            if agent.name not in self._agents:
                self._agents[agent.name] = agent
                new_agents.append(agent.name)
        
        # Save configuration
        self._save_configuration()
        
        logger.info(f"Added repository {repo_url} with {len(new_agents)} new agents")
        return new_agents
    
    def register_agent(self, agent: AgentDefinition) -> None:
        """Register a new agent."""
        self._agents[agent.name] = agent
        self._save_configuration()
        logger.info(f"Registered agent: {agent.name}")
    
    def unregister_agent(self, agent_name: str) -> bool:
        """Unregister an agent."""
        if agent_name in self._agents:
            del self._agents[agent_name]
            self._save_configuration()
            logger.info(f"Unregistered agent: {agent_name}")
            return True
        return False
    
    def list_agents(self) -> Dict[str, AgentDefinition]:
        """List all registered agents."""
        return self._agents.copy()
    
    def get_agent(self, agent_name: str) -> Optional[AgentDefinition]:
        """Get agent definition by name."""
        return self._agents.get(agent_name)
    
    async def execute_agent(
        self,
        agent_name: str,
        input_data: Any = None,
        config: Optional[Dict[str, Any]] = None,
        timeout: float = 30.0
    ) -> AgentResult:
        """Execute an agent with given input and configuration."""
        agent = self._agents.get(agent_name)
        if not agent:
            raise GitMCPError(f"Agent not found: {agent_name}")
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Prepare environment
            env = {**agent.env}
            if config:
                # Merge configuration into environment as JSON
                env['AGENT_CONFIG'] = json.dumps(config)
            
            # Prepare input
            input_text = ""
            if input_data is not None:
                if agent.input_format == 'json':
                    input_text = json.dumps(input_data)
                elif agent.input_format == 'yaml':
                    input_text = yaml.safe_dump(input_data)
                else:
                    input_text = str(input_data)
            
            # Execute agent
            process = await asyncio.create_subprocess_exec(
                agent.command,
                *agent.args,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(input_text.encode() if input_text else None),
                timeout=timeout
            )
            
            execution_time = asyncio.get_event_loop().time() - start_time
            
            # Parse output
            output = None
            if stdout:
                output_text = stdout.decode()
                if agent.output_format == 'json':
                    try:
                        output = json.loads(output_text)
                    except json.JSONDecodeError:
                        output = output_text
                elif agent.output_format == 'yaml':
                    try:
                        output = yaml.safe_load(output_text)
                    except yaml.YAMLError:
                        output = output_text
                else:
                    output = output_text
            
            success = process.returncode == 0
            error = stderr.decode() if stderr and not success else None
            
            result = AgentResult(
                agent_name=agent_name,
                success=success,
                output=output,
                error=error,
                execution_time=execution_time,
                metadata={
                    'return_code': process.returncode,
                    'timeout': timeout,
                    'input_format': agent.input_format,
                    'output_format': agent.output_format
                }
            )
            
            logger.info(f"Executed agent {agent_name}: success={success}, time={execution_time:.2f}s")
            return result
            
        except asyncio.TimeoutError:
            execution_time = asyncio.get_event_loop().time() - start_time
            return AgentResult(
                agent_name=agent_name,
                success=False,
                output=None,
                error=f"Agent execution timed out after {timeout} seconds",
                execution_time=execution_time,
                metadata={'timeout': True}
            )
        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            logger.error(f"Failed to execute agent {agent_name}: {e}")
            return AgentResult(
                agent_name=agent_name,
                success=False,
                output=None,
                error=str(e),
                execution_time=execution_time,
                metadata={'exception': type(e).__name__}
            )
    
    async def execute_agent_workflow(
        self,
        agent_names: List[str],
        initial_input: Any = None,
        config: Optional[Dict[str, Any]] = None
    ) -> List[AgentResult]:
        """Execute a workflow of multiple agents in sequence."""
        results = []
        current_input = initial_input
        
        for agent_name in agent_names:
            result = await self.execute_agent(agent_name, current_input, config)
            results.append(result)
            
            if not result.success:
                logger.warning(f"Agent {agent_name} failed, stopping workflow")
                break
            
            # Use output as input for next agent
            current_input = result.output
        
        return results
    
    def get_agents_by_trigger(self, trigger: str) -> List[str]:
        """Get agents that respond to a specific trigger."""
        matching_agents = []
        for name, agent in self._agents.items():
            if trigger in agent.triggers:
                matching_agents.append(name)
        return matching_agents
    
    def validate_agent_dependencies(self, agent_name: str) -> List[str]:
        """Validate agent dependencies and return missing ones."""
        agent = self._agents.get(agent_name)
        if not agent:
            return [f"Agent not found: {agent_name}"]
        
        missing_deps = []
        for dep in agent.dependencies:
            if dep not in self._agents:
                missing_deps.append(dep)
        
        return missing_deps


# Global agent service instance
_agent_service: Optional[AgentService] = None


def get_agent_service() -> AgentService:
    """Get the global agent service instance."""
    global _agent_service
    if _agent_service is None:
        _agent_service = AgentService()
    return _agent_service