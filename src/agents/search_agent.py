from create_agent import create_agent
from tools.FileEdit import create_document, read_document, collect_data
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from tools.internet import google_search, scrape_webpages_with_fallback
from langchain.agents import load_tools

def create_search_agent(llm, members, working_directory):
    """Create the search agent"""
    wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
    tools = [
        create_document, 
        read_document, 
        collect_data, 
        wikipedia, 
        google_search, 
        scrape_webpages_with_fallback
    ] + load_tools(["arxiv"],)
    
    system_prompt = """
    You are a skilled research assistant responsible for gathering and summarizing relevant information. Your main tasks include:

    1. Conducting thorough literature reviews using academic databases and reputable online sources.
    2. Summarizing key findings in a clear, concise manner.
    3. Providing citations for all sources, prioritizing peer-reviewed and academically reputable materials.

    Constraints:
    - Focus exclusively on information retrieval and summarization; do not engage in data analysis or processing.
    - Present information in an organized format, with clear attributions to sources.
    - Evaluate the credibility of sources and prioritize high-quality, reliable information.
    """
    return create_agent(
        llm,
        tools,
        system_prompt,
        members,
        working_directory
    )
