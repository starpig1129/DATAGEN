from pydantic import BaseModel, Field
from typing import Sequence , List

from langchain_core.messages import BaseMessage

from ..core.language_models import LanguageModelManager
from ..tools.FileEdit import read_document
from ..tools.basetool import list_directory
from .base import BaseAgent
from ..config import WORKING_DIRECTORY

class NoteState(BaseModel):
    """Pydantic model for the entire state structure."""
    messages: Sequence[BaseMessage] = Field(default_factory=list, description="List of message dictionaries")
    hypothesis: str = Field(default="", description="Current research hypothesis")
    process: str = Field(default="", description="Current research process")
    process_decision: str = Field(default="", description="Decision about the next process step")
    visualization_state: str = Field(default="", description="Current state of data visualization")
    searcher_state: str = Field(default="", description="Current state of the search process")
    code_state: str = Field(default="", description="Current state of code development")
    report_section: str = Field(default="", description="Content of the report sections")
    quality_review: str = Field(default="", description="Feedback from quality review")
    needs_revision: bool = Field(default=False, description="Flag indicating if revision is needed")
    sender: str = Field(default="", description="Identifier of the last message sender")

    class Config:
        arbitrary_types_allowed = True  # Allow BaseMessage type without explicit validator

class NoteAgent(BaseAgent):
    """Agent responsible for taking notes on the research process."""

    def __init__(self, language_model_manager: LanguageModelManager, team_members: List[str], working_directory: str = WORKING_DIRECTORY):
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
            response_format=NoteState
        )

    def _get_system_prompt(self) -> str:
        """Get the system prompt for NoteAgent."""
        return "SYSTEM_PROMPT:You are a meticulous research process note-taker. Your main responsibility is to observe, summarize, and document the actions and findings of the research team. Your tasks include:\n\n1. Observing and recording key activities, decisions, and discussions among team members.\n2. Summarizing complex information into clear, concise, and accurate notes.\n3. Organizing notes in a structured format that ensures easy retrieval and reference.\n4. Highlighting significant insights, breakthroughs, challenges, or any deviations from the research plan.\n5. Responding only in JSON format to ensure structured documentation.\n\nYour output should be well-organized and easy to integrate with other project documentation."

    def _get_tools(self):
        """Get the tools for NoteAgent."""
        return [read_document, list_directory]
