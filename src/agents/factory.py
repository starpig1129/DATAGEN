from .visualization_agent import VisualizationAgent
from .code_agent import CodeAgent
from .search_agent import SearchAgent
from .report_agent import ReportAgent
from .quality_review_agent import QualityReviewAgent
from .refiner_agent import RefinerAgent
from .hypothesis_agent import HypothesisAgent
from .process_agent import ProcessAgent
from .note_agent import NoteAgent
from ..load_cfg import WORKING_DIRECTORY

class AgentFactory:
    """A factory class for creating agents."""

    def __init__(self, language_model_manager, team_members, working_directory=WORKING_DIRECTORY):
        """
        Initialize the AgentFactory.

        Args:
            language_model_manager: Manager for language model configuration.
            team_members: List of team member roles for collaboration.
            working_directory: The directory where the agent's data will be stored.
        """
        self.language_model_manager = language_model_manager
        self.team_members = team_members
        self.working_directory = working_directory

    def create_agent(self, agent_name: str):
        """
        Creates an agent instance based on the agent name.

        Args:
            agent_name: The name of the agent to create.

        Returns:
            An instance of the requested agent.

        Raises:
            ValueError: If the agent creation is not implemented.
        """
        agent_mapping = {
            "visualization_agent": VisualizationAgent,
            "code_agent": CodeAgent,
            "searcher_agent": SearchAgent,
            "report_agent": ReportAgent,
            "quality_review_agent": QualityReviewAgent,
            "refiner_agent": RefinerAgent,
            "hypothesis_agent": HypothesisAgent,
            "process_agent": ProcessAgent,
            "note_agent": NoteAgent,
        }

        agent_class = agent_mapping.get(agent_name)
        if not agent_class:
            raise ValueError(f"Agent creation for '{agent_name}' is not implemented.")

        return agent_class(
            language_model_manager=self.language_model_manager,
            team_members=self.team_members,
            working_directory=self.working_directory
        )