import os
from abc import ABC, abstractmethod
from typing import List, Any

from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

from ..logger import setup_logger
from ..core.language_models import LanguageModelManager
from ..load_cfg import WORKING_DIRECTORY
logger = setup_logger()

class BaseAgent(ABC):
    """An abstract base class for all agents."""

    def __init__(
        self,
        agent_name: str,
        language_model_manager: LanguageModelManager,
        team_members: List[str],
        working_directory: str = WORKING_DIRECTORY
    ):
        """
        Initialize the base agent with common creation logic.

        Args:
            agent_name: The name of the agent for configuration lookup.
            language_model_manager: Manager for language model configuration.
            team_members: List of team member roles for collaboration.
            working_directory: The directory where the agent's data will be stored.
        """
        self.agent_name = agent_name
        self.language_model_manager = language_model_manager
        self.team_members = team_members
        self.working_directory = working_directory

        # Create the language model using the manager
        self.model = self._create_model()

        # Get agent-specific configuration from subclasses
        system_prompt = self._get_system_prompt()
        tools = self._get_tools()

        # Create the agent executor using the common create_agent function
        self.agent = self._create_base_agent(
            self.model,
            tools,
            system_prompt,
            team_members,
        )
    def _create_base_agent(
        self,
        model,
        tools: list,
        role_prompt: str,
        team_members: list[str],
        ):
            """Create an agent with the given parameters."""
            
            logger.info("Creating agent")

            # Prepare system prompt
            tool_names = ", ".join([tool.name for tool in tools])
            team_members_str = ", ".join(team_members)

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
                f"You are chosen for a reason! You are one of the following team members: {team_members_str}.\n"
                "Use the ListDirectoryContents tool to check for updates in the directory contents when needed."
            )

            # Create agent
            agent = create_agent(
                model=model,
                tools=tools,
                system_prompt=system_prompt
            )
            
            logger.info("Agent created successfully")
            return agent

    def _create_model(self) -> ChatOpenAI:
        """Create a model instance for this agent."""
        provider = self.language_model_manager.get_provider(self.agent_name)
        model_class = provider.get_model_class()
        config = self.language_model_manager.get_model_config(self.agent_name)
        return model_class(**config)

    def invoke(self, state: Any) -> Any:
        """
        Invokes the agent with a given state.

        Args:
            state: The current state of the workflow, accepts any input understood by the underlying agent.

        Returns:
            The agent's response (type may vary).
        """
        return self.agent.invoke(state)

    @abstractmethod
    def _get_system_prompt(self) -> str:
        """
        Get the system prompt specific to this agent.

        Returns:
            A string containing the system prompt.
        """
        pass

    @abstractmethod
    def _get_tools(self) -> List:
        """
        Get the list of tools specific to this agent.

        Returns:
            A list of tools the agent can use.
        """
        pass