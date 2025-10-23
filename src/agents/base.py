from abc import ABC, abstractmethod
from typing import List

from langchain.agents import AgentExecutor
from langchain_openai import ChatOpenAI

from ..create_agent import create_agent
from ..core.language_models import LanguageModelManager


class BaseAgent(ABC):
    """An abstract base class for all agents."""

    def __init__(
        self,
        agent_name: str,
        language_model_manager: LanguageModelManager,
        team_members: List[str],
        working_directory: str = './data_storage/'
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
        self.llm = self._create_model()

        # Get agent-specific configuration from subclasses
        system_prompt = self._get_system_prompt()
        tools = self._get_tools()

        # Create the agent executor using the common create_agent function
        self.agent_executor = create_agent(
            self.llm,
            tools,
            system_prompt,
            team_members,
            working_directory
        )

    def _create_model(self) -> ChatOpenAI:
        """Create a model instance for this agent."""
        provider = self.language_model_manager.get_provider(self.agent_name)
        model_class = provider.get_model_class()
        config = self.language_model_manager.get_model_config(self.agent_name)
        return model_class(**config)

    def invoke(self, state: dict) -> dict:
        """
        Invokes the agent with a given state.

        Args:
            state: The current state of the workflow.

        Returns:
            A dictionary representing the updated state.
        """
        return self.agent_executor.invoke(state)

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