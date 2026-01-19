"""MCP (Model Context Protocol) server manager.

This module provides management of MCP server connections and tool exposure
for agents. It follows the MCP specification for connecting to external
tools and resources.

Reference: https://modelcontextprotocol.io/

Example:
    manager = MCPManager()
    
    # Get tools for an agent
    tools = manager.get_tools_for_agent("process_agent")
    
    # List resources from a server
    resources = manager.list_resources("filesystem")
"""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from ..logger import setup_logger


logger = setup_logger()



# Constants
MCP_SERVER_STOP_TIMEOUT = 5


@dataclass
class MCPServerConfig:
    """Configuration for an MCP server.

    Attributes:
        name: Server identifier.
        command: Command to start the server.
        args: Command line arguments.
        env: Environment variables for the server.
        description: Human-readable description.
    """
    name: str
    command: str
    args: List[str] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)
    description: str = ""


@dataclass
class MCPResource:
    """A resource exposed by an MCP server.

    Attributes:
        uri: Unique resource identifier.
        name: Human-readable name.
        mime_type: MIME type of the resource.
        description: Optional description.
    """
    uri: str
    name: str
    mime_type: str = "text/plain"
    description: str = ""


@dataclass
class MCPTool:
    """A tool exposed by an MCP server.

    Attributes:
        name: Tool identifier.
        description: Human-readable description.
        input_schema: JSON schema for tool input.
        server_name: Name of the server providing this tool.
    """
    name: str
    description: str
    input_schema: Dict[str, Any] = field(default_factory=dict)
    server_name: str = ""


class MCPManager:
    """Manages MCP server connections and tool exposure.

    This manager handles:
    - Loading MCP server configurations
    - Starting and stopping MCP servers
    - Discovering tools and resources from servers
    - Providing tools to agents based on their configuration

    Attributes:
        config_path: Path to the MCP configuration file.
    """

    def __init__(self, config_path: str = "config/mcp.yaml") -> None:
        """Initialize the MCP manager.

        Args:
            config_path: Path to the MCP configuration file.
        """
        self.config_path = Path(config_path)
        self._config: Optional[Dict[str, Any]] = None
        self._servers: Dict[str, MCPServerConfig] = {}
        self._server_processes: Dict[str, subprocess.Popen] = {}

    @property
    def config(self) -> Dict[str, Any]:
        """Lazy-load MCP configuration.

        Returns:
            Configuration dictionary.
        """
        if self._config is None:
            self._config = self._load_config()
        return self._config

    def get_server_config(self, name: str) -> Optional[MCPServerConfig]:
        """Get configuration for a specific MCP server.

        Args:
            name: Server name.

        Returns:
            MCPServerConfig or None if not found.
        """
        if name in self._servers:
            return self._servers[name]

        servers = self.config.get("servers", {})
        if name not in servers:
            logger.warning(f"MCP server not found: {name}")
            return None

        server_config = servers[name]
        mcp_config = MCPServerConfig(
            name=name,
            command=server_config.get("command", ""),
            args=server_config.get("args", []),
            env=server_config.get("env", {}),
            description=server_config.get("description", ""),
        )
        self._servers[name] = mcp_config
        return mcp_config

    def get_enabled_servers(self, agent_name: str) -> List[MCPServerConfig]:
        """Get list of MCP servers enabled for an agent.

        Args:
            agent_name: Name of the agent.

        Returns:
            List of MCPServerConfig for enabled servers.
        """
        from .agent_config_loader import get_agent_config_loader

        loader = get_agent_config_loader()
        mcp_config = loader.load_mcp_config(agent_name)

        servers = []
        for name in mcp_config.get("servers", {}).keys():
            config = self.get_server_config(name)
            if config:
                servers.append(config)

        return servers

    def get_tools_for_agent(self, agent_name: str) -> List[MCPTool]:
        """Get all tools from MCP servers enabled for an agent.

        Note: This is a placeholder that returns tool metadata.
        Actual tool invocation requires running MCP servers.

        Args:
            agent_name: Name of the agent.

        Returns:
            List of MCPTool objects.
        """
        servers = self.get_enabled_servers(agent_name)
        tools = []

        for server in servers:
            # Add placeholder tools based on server type
            # In production, this would query the actual MCP server
            if server.name == "filesystem":
                tools.extend(self._get_filesystem_tools(server))
            elif server.name == "web-search":
                tools.extend(self._get_web_search_tools(server))
            elif server.name == "github":
                tools.extend(self._get_github_tools(server))

        return tools

    def list_resources(self, server_name: str) -> List[MCPResource]:
        """List available resources from an MCP server.

        Note: This is a placeholder. Actual resource listing requires
        a running MCP server connection.

        Args:
            server_name: Name of the MCP server.

        Returns:
            List of MCPResource objects.
        """
        config = self.get_server_config(server_name)
        if not config:
            return []

        # Placeholder - in production, query the actual server
        logger.info(f"Would list resources from {server_name}")
        return []

    def start_server(self, name: str) -> bool:
        """Start an MCP server process.

        Args:
            name: Server name.

        Returns:
            True if server started successfully.
        """
        if name in self._server_processes:
            logger.warning(f"MCP server already running: {name}")
            return True

        config = self.get_server_config(name)
        if not config:
            return False

        try:
            env = os.environ.copy()
            env.update(config.env)

            cmd = [config.command] + config.args
            process = subprocess.Popen(
                cmd,
                env=env,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self._server_processes[name] = process
            logger.info(f"Started MCP server: {name}")
            return True
        except Exception as e:
            logger.error(f"Failed to start MCP server {name}: {e}")
            return False

    def stop_server(self, name: str) -> None:
        """Stop an MCP server process.

        Args:
            name: Server name.
        """
        if name not in self._server_processes:
            return

        process = self._server_processes.pop(name)
        process.terminate()
        try:
            process.wait(timeout=MCP_SERVER_STOP_TIMEOUT)
        except subprocess.TimeoutExpired:
            process.kill()
        logger.info(f"Stopped MCP server: {name}")

    def stop_all_servers(self) -> None:
        """Stop all running MCP server processes."""
        for name in list(self._server_processes.keys()):
            self.stop_server(name)

    def _load_config(self) -> Dict[str, Any]:
        """Load MCP configuration from YAML file.

        Returns:
            Configuration dictionary.
        """
        if not self.config_path.exists():
            logger.warning(f"MCP config not found: {self.config_path}")
            return {"servers": {}, "defaults": []}

        try:
            content = self.config_path.read_text(encoding="utf-8")
            config = yaml.safe_load(content)
            return self._expand_env_vars(config)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse MCP config: {e}")
            return {"servers": {}, "defaults": []}

    def _expand_env_vars(self, obj: Any) -> Any:
        """Recursively expand environment variables in config.

        Args:
            obj: Configuration object.

        Returns:
            Object with environment variables expanded.
        """
        import re

        if isinstance(obj, dict):
            return {k: self._expand_env_vars(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._expand_env_vars(item) for item in obj]
        elif isinstance(obj, str):
            pattern = re.compile(r"\$\{([^}]+)\}")
            def replace(match):
                var_name = match.group(1)
                return os.environ.get(var_name, match.group(0))
            return pattern.sub(replace, obj)
        return obj

    def _get_filesystem_tools(self, server: MCPServerConfig) -> List[MCPTool]:
        """Get placeholder tools for filesystem server.

        Args:
            server: Server configuration.

        Returns:
            List of filesystem tools.
        """
        return [
            MCPTool(
                name="read_file",
                description="Read contents of a file",
                input_schema={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "File path"}
                    },
                    "required": ["path"]
                },
                server_name=server.name,
            ),
            MCPTool(
                name="write_file",
                description="Write contents to a file",
                input_schema={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "File path"},
                        "content": {"type": "string", "description": "File content"}
                    },
                    "required": ["path", "content"]
                },
                server_name=server.name,
            ),
            MCPTool(
                name="list_directory",
                description="List contents of a directory",
                input_schema={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Directory path"}
                    },
                    "required": ["path"]
                },
                server_name=server.name,
            ),
        ]

    def _get_web_search_tools(self, server: MCPServerConfig) -> List[MCPTool]:
        """Get placeholder tools for web search server.

        Args:
            server: Server configuration.

        Returns:
            List of web search tools.
        """
        return [
            MCPTool(
                name="web_search",
                description="Search the web for information",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"}
                    },
                    "required": ["query"]
                },
                server_name=server.name,
            ),
        ]

    def _get_github_tools(self, server: MCPServerConfig) -> List[MCPTool]:
        """Get placeholder tools for GitHub server.

        Args:
            server: Server configuration.

        Returns:
            List of GitHub tools.
        """
        return [
            MCPTool(
                name="search_repositories",
                description="Search GitHub repositories",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"}
                    },
                    "required": ["query"]
                },
                server_name=server.name,
            ),
            MCPTool(
                name="get_file_contents",
                description="Get contents of a file from a repository",
                input_schema={
                    "type": "object",
                    "properties": {
                        "owner": {"type": "string", "description": "Repository owner"},
                        "repo": {"type": "string", "description": "Repository name"},
                        "path": {"type": "string", "description": "File path"}
                    },
                    "required": ["owner", "repo", "path"]
                },
                server_name=server.name,
            ),
        ]


# Singleton instance
_default_manager: Optional[MCPManager] = None


def get_mcp_manager() -> MCPManager:
    """Get the default MCPManager singleton.

    Returns:
        MCPManager instance.
    """
    global _default_manager
    if _default_manager is None:
        _default_manager = MCPManager()
    return _default_manager
