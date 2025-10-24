from typing import Literal
from pydantic import BaseModel, Field

from ..tools.basetool import list_directory
from ..tools.FileEdit import create_document, read_document, edit_document
from .base import BaseAgent
from ..load_cfg import WORKING_DIRECTORY

class QualityOutput(BaseModel):
    """Pydantic model for quality review output."""
    next: Literal["CONTINUE", "REVISION"] = Field(
        description="Indicates whether to continue or request revision"
    )
    feedback: str = Field(
        description="Specific feedback on parts that need improvement"
    )

class QualityReviewAgent(BaseAgent):
    """Agent responsible for reviewing and ensuring the quality of research outputs."""

    def __init__(self, language_model_manager, team_members, working_directory=WORKING_DIRECTORY):
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
            working_directory=working_directory
        )

    def _get_system_prompt(self) -> str:
        """Get the system prompt for quality review."""
        return '''
        You are a meticulous quality control expert responsible for reviewing and ensuring the high standard of all research outputs. Your tasks include:

        1. Critically evaluating the content, methodology, and conclusions of research reports.
        2. Checking for consistency, accuracy, and clarity in all documents.
        3. Identifying areas that need improvement or further elaboration.
        4. Ensuring adherence to scientific writing standards and ethical guidelines.

        After your review, if revisions are needed, respond with 'REVISION' as a prefix, set needs_revision=True, and provide specific feedback on parts that need improvement. If no revisions are necessary, respond with 'CONTINUE' as a prefix and set needs_revision=False.
        '''

    def _get_tools(self):
        """Get the list of tools for quality review."""
        return [create_document, read_document, edit_document, list_directory]
