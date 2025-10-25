from typing import List

from ..core.language_models import LanguageModelManager
from ..tools.basetool import list_directory
from ..tools.FileEdit import create_document, read_document, edit_document
from .base import BaseAgent
from ..config import WORKING_DIRECTORY


class ReportAgent(BaseAgent):
    """Agent responsible for drafting comprehensive research reports."""

    def __init__(self, language_model_manager: LanguageModelManager, team_members: List[str], working_directory: str = WORKING_DIRECTORY):
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

    def _get_system_prompt(self) -> str:
        """Get the system prompt for report writing."""
        return '''
        You are an experienced scientific writer tasked with drafting comprehensive research reports. Your primary duties include:

        1. Clearly stating the research hypothesis and objectives in the introduction.
        2. Detailing the methodology used, including data collection and analysis techniques.
        3. Structuring the report into coherent sections (e.g., Introduction, Methodology, Results, Discussion, Conclusion).
        4. Synthesizing information from various sources into a unified narrative.
        5. Integrating relevant data visualizations and ensuring they are appropriately referenced and explained.

        Constraints:
        - Focus solely on report writing; do not perform data analysis or create visualizations.
        - Maintain an objective, academic tone throughout the report.
        - Cite all sources using APA style and ensure that all findings are supported by evidence.
        '''

    def _get_tools(self):
        """Get the list of tools for report writing."""
        return [create_document, read_document, edit_document,list_directory]
