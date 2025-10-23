from create_agent import create_agent
from tools.FileEdit import collect_data
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from tools.internet import google_search, scrape_webpages_with_fallback
from langchain.agents import load_tools

def create_hypothesis_agent(llm, members, working_directory):
    """Create the hypothesis agent"""
    wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
    base_tools = [
        collect_data, 
        wikipedia, 
        google_search, 
        scrape_webpages_with_fallback
    ] + load_tools(["arxiv"],)
    
    system_prompt = '''
    As an esteemed expert in data analysis, your task is to formulate a set of research hypotheses and outline the steps to be taken based on the information table provided. Utilize statistics, machine learning, deep learning, and artificial intelligence in developing these hypotheses. Your hypotheses should be precise, achievable, professional, and innovative. To ensure the feasibility and uniqueness of your hypotheses, thoroughly investigate relevant information. For each hypothesis, include ample references to support your claims.

    Upon analyzing the information table, you are required to:

    1. Formulate research hypotheses that leverage statistics, machine learning, deep learning, and AI techniques.
    2. Outline the steps involved in testing these hypotheses.
    3. Verify the feasibility and uniqueness of each hypothesis through a comprehensive literature review.

    At the conclusion of your analysis, present the complete research hypotheses, elaborate on their uniqueness and feasibility, and provide relevant references to support your assertions. Please answer in structured way to enhance readability.
    Just answer a research hypothesis.
    '''

    return create_agent(
        llm, 
        base_tools,
        system_prompt,
        members,
        working_directory
    )
