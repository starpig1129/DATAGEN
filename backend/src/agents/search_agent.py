from typing import List

from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_community.agent_toolkits.load_tools import load_tools

from ..core.language_models import LanguageModelManager
from .base import BaseAgent
from ..tools.basetool import list_directory
from ..tools.FileEdit import create_document, read_document, collect_data
from ..tools.internet import google_search, scrape_webpages
from ..config import WORKING_DIRECTORY

class SearchAgent(BaseAgent):
    """Agent responsible for gathering and summarizing research information."""

    def __init__(self, language_model_manager: LanguageModelManager, team_members: List[str], working_directory: str = WORKING_DIRECTORY):
        """
        Initialize the SearchAgent.

        Args:
            language_model_manager: Manager for language model configuration.
            team_members: List of team member roles for collaboration.
            working_directory: The directory where the agent's data will be stored.
        """
        super().__init__(
            agent_name="searcher_agent",
            language_model_manager=language_model_manager,
            team_members=team_members,
            working_directory=working_directory
        )

    def _get_system_prompt(self) -> str:
        """Get the system prompt for information retrieval and summarization."""
        return '''
        You are a skilled research assistant responsible for gathering and summarizing relevant information. Your main tasks include:

        1. Conducting thorough literature reviews using academic databases and reputable online sources.
        2. Summarizing key findings in a clear, concise manner.
        3. Providing citations for all sources, prioritizing peer-reviewed and academically reputable materials.

        Constraints:
        - Focus exclusively on information retrieval and summarization; do not engage in data analysis or processing.
        - Present information in an organized format, with clear attributions to sources.
        - Evaluate the credibility of sources and prioritize high-quality, reliable information.
        '''

    def _get_tools(self):
        """Get the list of tools for information retrieval and summarization."""
        api_wrapper = WikipediaAPIWrapper(wiki_client=None)
        wikipedia = WikipediaQueryRun(api_wrapper=api_wrapper)
        base_tools = [
            create_document,
            read_document,
            collect_data,
            wikipedia,
            google_search,
            scrape_webpages,
            list_directory
        ] + load_tools(["arxiv"])

        return base_tools
