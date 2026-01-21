from typing import Literal, List, TYPE_CHECKING
from pydantic import BaseModel, Field

from ..tools.basetool import list_directory
from ..tools.FileEdit import create_document, read_document, edit_document
from .base import BaseAgent
from ..config import WORKING_DIRECTORY

if TYPE_CHECKING:
    from ..core.language_models import LanguageModelManager

class QualityOutput(BaseModel):
    """Pydantic model for quality review output."""
    needs_revision: bool = Field(
        description="Indicates if needs revision"
    )
    feedback: str = Field(
        description="Specific feedback on parts that need improvement"
    )

class QualityReviewAgent(BaseAgent):
    """Agent responsible for reviewing and ensuring the quality of research outputs."""

    def __init__(self, language_model_manager: "LanguageModelManager", team_members: List[str], working_directory: str = WORKING_DIRECTORY):
        """
        Initialize the QualityReviewAgent.

        Args:
            language_model_manager: Manager for language model configuration.
            team_members: List of team member roles for collaboration.
            working_directory: The directory where the agent's data will be stored.
        """
        super().__init__(
            agent_name="quality_review_agent", 
            language_model_manager=language_model_manager, 
            team_members=team_members, 
            working_directory=working_directory, 
            response_format=QualityOutput
        )

    def _get_tools(self) -> List:
        """Get the list of tools for the QualityReviewAgent."""
        return [create_document, read_document, edit_document, list_directory]

