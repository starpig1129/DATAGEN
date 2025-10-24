from typing import List

from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_community.agent_toolkits.load_tools import load_tools

from .base import BaseAgent
from ..tools.basetool import list_directory
from ..tools.FileEdit import collect_data
from ..tools.internet import google_search, scrape_webpages
from ..config import WORKING_DIRECTORY
from ..core.language_models import LanguageModelManager

class HypothesisAgent(BaseAgent):
    """Agent responsible for generating research hypotheses."""

    def __init__(self, language_model_manager: LanguageModelManager, team_members: List[str], working_directory: str = WORKING_DIRECTORY):
        """
        Initialize the HypothesisAgent.

        Args:
            language_model_manager: Manager for language model configuration.
            team_members: List of team member roles for collaboration.
            working_directory: The directory where the agent's data will be stored.
        """
        super().__init__(
            agent_name="hypothesis_agent",
            language_model_manager=language_model_manager,
            team_members=team_members,
            working_directory=working_directory
        )

    def _get_system_prompt(self) -> str:
        """Get the system prompt for hypothesis generation."""
        return '''
        As an esteemed expert in data analysis, your task is to formulate a set of research hypotheses and outline the steps to be taken based on the information table provided. Utilize statistics, machine learning, deep learning, and artificial intelligence in developing these hypotheses. Your hypotheses should be precise, achievable, professional, and innovative. To ensure the feasibility and uniqueness of your hypotheses, thoroughly investigate relevant information. For each hypothesis, include ample references to support your claims.

        Upon analyzing the information table, you are required to:

        1. Formulate research hypotheses that leverage statistics, machine learning, deep learning, and AI techniques.
        2. Outline the steps involved in testing these hypotheses.
        3. Verify the feasibility and uniqueness of each hypothesis through a comprehensive literature review.

        At the conclusion of your analysis, present the complete research hypotheses, elaborate on their uniqueness and feasibility, and provide relevant references to support your assertions. Please answer in structured way to enhance readability.
        Just answer a research hypothesis.
        '''

    def _get_tools(self):
        """Get the list of tools for hypothesis generation."""
        api_wrapper = WikipediaAPIWrapper(wiki_client=None)
        wikipedia = WikipediaQueryRun(api_wrapper=api_wrapper)
        base_tools = [
            collect_data,
            wikipedia,
            google_search,
            scrape_webpages,
            list_directory
        ] + load_tools(["arxiv"])

        return base_tools
