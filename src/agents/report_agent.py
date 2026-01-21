from typing import List, TYPE_CHECKING

from ..tools.basetool import list_directory
from ..tools.FileEdit import create_document, read_document, edit_document
from .base import BaseAgent
from ..config import WORKING_DIRECTORY
from ..core.schemas import ArtifactSchema

if TYPE_CHECKING:
    from ..core.language_models import LanguageModelManager

class ReportAgent(BaseAgent):
    """Agent responsible for drafting comprehensive research reports."""

    def __init__(self, language_model_manager: "LanguageModelManager", team_members: List[str], working_directory: str = WORKING_DIRECTORY):
        """
        Initialize the ReportAgent.

        Args:
            language_model_manager: Manager for language model configuration.
            team_members: List of team member roles for collaboration.
            working_directory: The directory where the agent's data will be stored.
        """
        super().__init__(
            agent_name="report_agent",
            language_model_manager=language_model_manager,
            team_members=team_members,
            working_directory=working_directory
        )
        self.response_format = ArtifactSchema

    def _get_tools(self) -> List:
        """Get the list of tools for report writing."""
        return [create_document, read_document, edit_document,list_directory]
