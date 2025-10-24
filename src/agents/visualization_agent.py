from typing import List

from ..core.language_models import LanguageModelManager
from ..tools.basetool import execute_code, execute_command, list_directory
from ..tools.FileEdit import read_document
from .base import BaseAgent
from ..config import WORKING_DIRECTORY

class VisualizationAgent(BaseAgent):
    """Agent responsible for creating data visualizations."""

    def __init__(self, language_model_manager: LanguageModelManager, team_members: List[str], working_directory: str = WORKING_DIRECTORY):
        """
        Initialize the VisualizationAgent.

        Args:
            language_model_manager: Manager for language model configuration.
            team_members: List of team member roles for collaboration.
            working_directory: The directory where the agent's data will be stored.
        """
        super().__init__(
            agent_name="visualization_agent",
            language_model_manager=language_model_manager,
            team_members=team_members,
            working_directory=working_directory
        )

    def _get_system_prompt(self) -> str:
        """Get the system prompt for data visualization."""
        return '''
        You are a data visualization expert tasked with creating insightful visual representations of data. Your primary responsibilities include:

        1. Designing appropriate visualizations that clearly communicate data trends and patterns.
        2. Selecting the most suitable chart types (e.g., bar charts, scatter plots, heatmaps) for different data types and analytical purposes.
        3. Providing executable Python code (using libraries such as matplotlib, seaborn, or plotly) that generates these visualizations.
        4. Including well-defined titles, axis labels, legends, and saving the visualizations as files.
        5. Offering brief but clear interpretations of the visual findings.

        **File Saving Guidelines:**
        - Save all visualizations as files with descriptive and meaningful filenames.
        - Ensure filenames are structured to easily identify the content (e.g., 'sales_trends_2024.png' for a sales trend chart).
        - Confirm that the saved files are organized in the working directory, making them easy for other agents to locate and use.

        **Constraints:**
        - Focus solely on visualization tasks; do not perform data analysis or preprocessing.
        - Ensure all visual elements are suitable for the target audience, with attention to color schemes and design principles.
        - Avoid over-complicating visualizations; aim for clarity and simplicity.
        '''

    def _get_tools(self):
        """Get the list of tools for data visualization."""
        return [read_document, execute_code, execute_command, list_directory]
