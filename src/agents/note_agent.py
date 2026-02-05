from pydantic import BaseModel, Field
from typing import Sequence , List, TYPE_CHECKING

from langchain_core.messages import BaseMessage

from ..tools.FileEdit import read_document
from ..tools.basetool import list_directory
from .base import BaseAgent
from ..config import WORKING_DIRECTORY
from ..core.state import State

if TYPE_CHECKING:
    from ..core.language_models import LanguageModelManager


class NoteAgent(BaseAgent):
    """Agent responsible for taking notes on the research process."""

    def __init__(self, language_model_manager: "LanguageModelManager", team_members: List[str], working_directory: str = WORKING_DIRECTORY):
        """
        Initialize the NoteAgent.

        Args:
            language_model_manager: Manager for language model configuration.
            team_members: List of team member roles for collaboration.
            working_directory: The directory where the agent's data will be stored.
        """
        super().__init__(
            agent_name="note_agent",
            language_model_manager=language_model_manager,
            team_members=team_members,
            working_directory=working_directory,
            response_format=State
        )

    def _get_tools(self) -> List:
        """Get the tools for NoteAgent."""
        return [read_document, list_directory]
