from typing import List

from ..tools.basetool import execute_code, execute_command, list_directory
from ..tools.FileEdit import read_document
from .base import BaseAgent
from ..config import WORKING_DIRECTORY
from ..core.language_models import LanguageModelManager

class CodeAgent(BaseAgent):
    """Agent responsible for writing and executing Python code for data processing."""

    def __init__(self, language_model_manager: LanguageModelManager, team_members: List[str], working_directory: str = WORKING_DIRECTORY):
        """
        Initialize the CodeAgent.

        Args:
            language_model_manager: Manager for language model configuration.
            team_members: List of team member roles for collaboration.
            working_directory: The directory where the agent's data will be stored.
        """
        super().__init__(
            agent_name="code_agent",
            language_model_manager=language_model_manager,
            team_members=team_members,
            working_directory=working_directory
        )

    def _get_system_prompt(self) -> str:
        """Get the system prompt for code generation and execution."""
        return '''
        You are an expert Python programmer specializing in data processing and analysis. Your main responsibilities include:

        1. Writing clean, efficient Python code for data manipulation, cleaning, and transformation.
        2. Implementing statistical methods and machine learning algorithms as needed.
        3. Debugging and optimizing existing code for performance improvements.
        4. Adhering to PEP 8 standards and ensuring code readability with meaningful variable and function names.

        Constraints:
        - Focus solely on data processing tasks; do not generate visualizations or write non-Python code.
        - Provide only valid, executable Python code, including necessary comments for complex logic.
        - Avoid unnecessary complexity; prioritize readability and efficiency.
        '''

    def _get_tools(self):
        """Get the list of tools for code generation and execution."""
        return [read_document, execute_code, execute_command, list_directory]
