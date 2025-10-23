from create_agent import create_agent
from tools.FileEdit import create_document, read_document, edit_document
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from tools.internet import google_search, scrape_webpages_with_fallback
from langchain.agents import load_tools

def create_refiner_agent(power_llm, members, working_directory):
    """Create the refiner agent"""
    wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
    tools = [
        create_document, 
        read_document, 
        edit_document,
        wikipedia, 
        google_search, 
        scrape_webpages_with_fallback
    ] + load_tools(["arxiv"],)
    
    system_prompt = '''
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
    return create_agent(
        power_llm,
        tools,
        system_prompt,
        members,
        working_directory
    )
