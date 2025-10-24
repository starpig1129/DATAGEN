from typing import List

from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_community.agent_toolkits.load_tools import load_tools

from ..core.language_models import LanguageModelManager
from .base import BaseAgent
from  ..tools.basetool import list_directory
from ..tools.internet import google_search, scrape_webpages
from ..tools.FileEdit import create_document, read_document, edit_document
from ..config import WORKING_DIRECTORY

class RefinerAgent(BaseAgent):
    """Agent responsible for optimizing and enhancing research reports."""

    def __init__(self, language_model_manager: LanguageModelManager, team_members: List[str], working_directory: str = WORKING_DIRECTORY):
        """
        Initialize the RefinerAgent.

        Args:
            language_model_manager: Manager for language model configuration.
            team_members: List of team member roles for collaboration.
            working_directory: The directory where the agent's data will be stored.
        """
        super().__init__(
            agent_name="refiner_agent",
            language_model_manager=language_model_manager,
            team_members=team_members,
            working_directory=working_directory
        )

    def _get_system_prompt(self) -> str:
        """Get the system prompt for report refinement."""
        return '''
        You are an expert AI report refiner tasked with optimizing and enhancing research reports. Your responsibilities include:

        1. Thoroughly reviewing the entire research report, focusing on content, structure, and readability.
        2. Identifying and emphasizing key findings, insights, and conclusions.
        3. Restructuring the report to improve clarity, coherence, and logical flow.
        4. Ensuring that all sections are well-integrated and support the primary research hypothesis.
        5. Condensing redundant or repetitive content while preserving essential details.
        6. Enhancing the overall readability, ensuring the report is engaging and impactful.

        Refinement Guidelines:
        - Maintain the scientific accuracy and integrity of the original content.
        - Ensure all critical points from the original report are preserved and clearly articulated.
        - Improve the logical progression of ideas and arguments.
        - Highlight the most significant results and their implications for the research hypothesis.
        - Ensure that the refined report aligns with the initial research objectives and hypothesis.

        After refining the report, submit it for final human review, ensuring it is ready for publication or presentation.
        '''

    def _get_tools(self):
        """Get the list of tools for report refinement."""
        api_wrapper = WikipediaAPIWrapper(wiki_client=None)
        wikipedia = WikipediaQueryRun(api_wrapper=api_wrapper)
        base_tools = [
            create_document,
            read_document,
            edit_document,
            wikipedia,
            google_search,
            scrape_webpages,
            list_directory
        ] + load_tools(["arxiv"])

        return base_tools
