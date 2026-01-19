"""Base agent class with external configuration support.

This module provides the abstract base class for all agents in the system.
It integrates with the AgentConfigLoader for external system prompts and
supports fallback to hardcoded prompts for backward compatibility.
"""

import os
from abc import ABC, abstractmethod
from typing import Any, List, Optional

from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

from ..logger import setup_logger
from ..core.language_models import LanguageModelManager
from ..config import WORKING_DIRECTORY

logger = setup_logger()


class BaseAgent(ABC):
    """An abstract base class for all agents.

    Supports both external configuration (via AgentConfigLoader) and
    hardcoded system prompts for backward compatibility.

    Attributes:
        agent_name: The name of the agent for configuration lookup.
        language_model_manager: Manager for language model configuration.
        team_members: List of team member roles for collaboration.
        working_directory: The directory where the agent's data will be stored.
        response_format: Optional format specification for structured output.
    """


    # Constants
    SYSTEM_PROMPT_PREFIX = "SYSTEM_PROMPT:"

    # Class-level config loader (shared across all agents)
    _config_loader: Optional["AgentConfigLoader"] = None

    @classmethod
    def get_config_loader(cls) -> "AgentConfigLoader":
        """Get or create the shared AgentConfigLoader instance.

        Returns:
            AgentConfigLoader instance.
        """
        if cls._config_loader is None:
            from ..core.agent_config_loader import AgentConfigLoader
            cls._config_loader = AgentConfigLoader()
        return cls._config_loader

    def __init__(
        self,
        agent_name: str,
        language_model_manager: LanguageModelManager,
        team_members: List[str],
        working_directory: str = WORKING_DIRECTORY,
        response_format: Any = None
    ) -> None:
        """Initialize the base agent with common creation logic.

        Args:
            agent_name: The name of the agent for configuration lookup.
            language_model_manager: Manager for language model configuration.
            team_members: List of team member roles for collaboration.
            working_directory: The directory where the agent's data will be stored.
            response_format: Optional format specification for structured output.
        """
        self.agent_name = agent_name
        self.language_model_manager = language_model_manager
        self.team_members = team_members
        self.working_directory = working_directory
        self.response_format = response_format

        # Create the language model using the manager
        self.model = self._create_model()

        # Get agent-specific configuration - try external config first, fallback to hardcoded
        role_prompt = self._load_system_prompt()
        tools = self._get_tools()

        # Check for skills and add LookupSkill tool if needed
        try:
            loader = self.get_config_loader()
            metadata = loader.load_metadata(self.agent_name)
            if metadata.skills:
                from ..tools.skills import LookupSkill
                tools.append(LookupSkill())
                logger.info(f"Added LookupSkill tool for {self.agent_name}")
        except Exception as e:
            logger.warning(f"Failed to check skills for {self.agent_name}: {e}")

        # Create the agent executor using the common create_agent function
        self.agent = self._create_base_agent(
            self.model,
            tools,
            role_prompt,
            team_members,
            response_format,
        )
    def _create_base_agent(
        self,
        model,
        tools: list,
        role_prompt: str,
        team_members: list[str],
        response_format: Any = None,
    ):
        """Create an agent with the given parameters.

        Args:
            model: The language model to use for the agent.
            tools: List of tools available to the agent.
            role_prompt: The role prompt defining the agent's behavior.
            team_members: List of team member roles for collaboration.
            response_format: Optional format specification for structured output.
        """
        
        # Prepare system prompt
        tool_names = ", ".join([tool.name for tool in tools])
        team_members_str = ", ".join(team_members)

        # Check if role_prompt contains a complete system prompt
        if role_prompt.startswith(self.SYSTEM_PROMPT_PREFIX):
            # Use the complete system prompt directly (remove the prefix)
            system_prompt = role_prompt[len(self.SYSTEM_PROMPT_PREFIX):]
        else:
            # Use the existing system prompt composition logic
            system_prompt = (
                "You are a specialized AI assistant in a data analysis team. "
                "Your role is to complete specific tasks in the research process. "
                "Use the provided tools to make progress on your task. "
                "If you can't fully complete a task, explain what you've done and what's needed next. "
                "Always aim for accurate and clear outputs. "
                f"You have access to the following tools: {tool_names}. "
                f"Your specific role: {role_prompt}\n"
                "Work autonomously according to your specialty, using the tools available to you. "
                "Do not ask for clarification. "
                "Your other team members (and other teams) will collaborate with you based on their specialties. "
                f"You are chosen for a reason! You are {self.agent_name} of the following team members: {team_members_str}.\n"
                "Use the ListDirectoryContents tool to check for updates in the directory contents when needed."
            )

        # Create agent
        agent = create_agent(
            model=model,
            tools=tools,
            system_prompt=system_prompt,
            response_format=response_format
        )

        logger.info(f"{self.agent_name} created successfully")
        return agent

    def _create_model(self) -> ChatOpenAI:
        """Create a model instance for this agent.

        Returns:
            Configured language model instance.
        """
        provider = self.language_model_manager.get_provider(self.agent_name)
        model_class = provider.get_model_class()
        config = self.language_model_manager.get_model_config(self.agent_name)
        return model_class(**config)

    def invoke(self, state: Any) -> Any:
        """Invoke the agent with a given state.

        Args:
            state: The current state of the workflow.

        Returns:
            The agent's response (type may vary).
        """
        return self.agent.invoke(state)

    def _load_system_prompt(self) -> str:
        """Load system prompt from external config or fallback to hardcoded.

        This method implements a two-stage loading strategy:
        1. Try to load from external AGENT.md configuration
        2. Fall back to the subclass's _get_system_prompt() method

        Returns:
            System prompt string.
        """
        try:
            loader = self.get_config_loader()
            prompt = loader.load_system_prompt(self.agent_name)
            logger.info(f"Loaded external config for {self.agent_name}")
            return prompt
        except FileNotFoundError:
            # Fallback to hardcoded prompt from subclass
            logger.debug(
                f"No external config for {self.agent_name}, using hardcoded prompt"
            )
            return self._get_system_prompt()
        except Exception as e:
            logger.warning(
                f"Failed to load external config for {self.agent_name}: {e}, "
                "falling back to hardcoded prompt"
            )
            return self._get_system_prompt()

    def _get_system_prompt(self) -> str:
        """Get the hardcoded system prompt for this agent.

        Subclasses can override this to provide a fallback system prompt
        when external configuration is not available.

        Returns:
            A string containing the system prompt.
        """
        return ""

    @abstractmethod
    def _get_tools(self) -> List:
        """Get the list of tools specific to this agent.

        Returns:
            A list of tools the agent can use.
        """
        pass