from core.create_agent import create_agent
from tools.FileEdit import collect_data
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from tools.internet import google_search, scrape_webpages_with_fallback
from langchain.agents import load_tools

def create_hypothesis_agent(llm, members, working_directory):
    """Create the hypothesis agent"""
    # 修復：為了測試和演示，暫時移除可能導致網路延遲的外部工具
    # 保留核心數據收集工具，但移除可能造成超時的網路查詢工具
    base_tools = [
        collect_data
        # 注釋掉可能導致延遲的外部工具以提高測試穩定性
        # wikipedia,
        # google_search,
        # scrape_webpages_with_fallback
    ]  # + load_tools(["arxiv"],)
    
    system_prompt = '''
    作為數據分析專家，請基於提供的數據快速生成研究假設。

    任務：
    1. 分析數據特徵和模式
    2. 提出2-3個可測試的研究假設
    3. 簡要說明驗證方法

    要求：
    - 保持假設簡潔明確
    - 基於統計學和機器學習方法
    - 確保假設可操作性

    請以結構化方式回答，專注於核心假設內容。
    '''

    return create_agent(
        llm, 
        base_tools,
        system_prompt,
        members,
        working_directory
    )
