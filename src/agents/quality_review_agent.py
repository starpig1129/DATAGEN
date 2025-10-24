from typing import Literal, List
from pydantic import BaseModel, Field

from ..tools.basetool import list_directory
from ..tools.FileEdit import create_document, read_document, edit_document
from .base import BaseAgent
from ..config import WORKING_DIRECTORY
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

    def __init__(self, language_model_manager: LanguageModelManager, team_members: List[str], working_directory: str = WORKING_DIRECTORY):
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

    def _get_system_prompt(self) -> str:
        """Get the system prompt for the QualityReviewAgent."""
        return '''
        You are a meticulous quality control expert responsible for reviewing and ensuring the high standard of all research outputs.
        
        Your tasks include:

        1. Critically evaluating the content, methodology, and conclusions of research reports.
        2. Checking for consistency, accuracy, and clarity in all documents.
        3. Identifying areas that need improvement or further elaboration.
        4. Ensuring adherence to scientific writing standards and ethical guidelines.
        5. Collaborating with other agents to gather necessary information for a comprehensive review.
        6. Provide detailed feedback on any deficiencies found and recommend specific revisions to enhance the overall quality of the research outputs.
        '''

    def _get_tools(self) -> List:
        """Get the list of tools for the QualityReviewAgent."""
        return [create_document, read_document, edit_document, list_directory]

