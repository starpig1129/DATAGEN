from typing import Any, Dict, List, Optional
from langchain.tools import BaseTool

from .basetool import execute_code, execute_command, list_directory
from .FileEdit import create_document, read_document, edit_document, collect_data
from .internet import google_search, scrape_webpages
from ..logger import setup_logger

from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_community.agent_toolkits.load_tools import load_tools

logger = setup_logger()

# Initialize complex tools
try:
    api_wrapper = WikipediaAPIWrapper(wiki_client=None)
    wikipedia = WikipediaQueryRun(api_wrapper=api_wrapper)
except Exception as e:
    logger.warning(f"Failed to initialize Wikipedia tool: {e}")
    wikipedia = None

try:
    arxiv_tools = load_tools(["arxiv"])
    arxiv = arxiv_tools[0] if arxiv_tools else None
except Exception as e:
    logger.warning(f"Failed to initialize Arxiv tool: {e}")
    arxiv = None

class ToolFactory:
    """Factory for creating and retrieving tool instances by name."""

    _registry = {
        "execute_code": execute_code,
        "execute_command": execute_command,
        "list_directory": list_directory,
        "create_document": create_document,
        "read_document": read_document,
        "edit_document": edit_document,
        "collect_data": collect_data,
        "google_search": google_search,
        "scrape_webpages": scrape_webpages,
        "wikipedia": wikipedia,
        "arxiv": arxiv,
    }

    @classmethod
    def get_tool(cls, tool_name: str) -> Optional[BaseTool]:
        """Get a tool instance by name.

        Args:
            tool_name: The name of the tool to retrieve.

        Returns:
            The tool instance or None if not found.
        """
        tool = cls._registry.get(tool_name)
        if not tool:
            logger.warning(f"Tool not found in registry: {tool_name}")
            return None
        return tool

    @classmethod
    def get_tools(cls, tool_names: List[str]) -> List[BaseTool]:
        """Get a list of tool instances by names.

        Args:
            tool_names: List of tool names to retrieve.

        Returns:
            List of tool instances. Logs warning for any missing tools.
        """
        tools = []
        for name in tool_names:
            tool = cls.get_tool(name)
            if tool:
                tools.append(tool)
        return tools

    @classmethod
    def list_available_tools(cls) -> List[str]:
        """List all available tool names in the registry."""
        return list(cls._registry.keys())

    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        """Get current tool configuration.
        
        Returns:
            Dictionary with all tool limits and settings.
        """
        from .tool_config import TOOL_CONFIG
        return TOOL_CONFIG.to_dict()

    @classmethod
    def get_limits(cls) -> Dict[str, Any]:
        """Get current execution and file operation limits.
        
        Returns:
            Dictionary with timeout, memory, and file size limits.
        """
        from .tool_config import TOOL_CONFIG
        return {
            "execution": {
                "timeout_seconds": TOOL_CONFIG.execution.timeout_seconds,
                "max_memory_mb": TOOL_CONFIG.execution.max_memory_mb,
                "max_output_chars": TOOL_CONFIG.execution.max_output_chars,
                "progress_timeout_seconds": TOOL_CONFIG.execution.progress_timeout_seconds,
            },
            "file_operations": {
                "max_read_bytes": TOOL_CONFIG.file_ops.max_read_bytes,
                "max_read_lines": TOOL_CONFIG.file_ops.max_read_lines,
                "max_write_bytes": TOOL_CONFIG.file_ops.max_write_bytes,
            },
            "security_scan_enabled": TOOL_CONFIG.enable_security_scan,
            "write_validation_enabled": TOOL_CONFIG.enable_write_validation,
        }
