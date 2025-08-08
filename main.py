#!/usr/bin/env python3

import os
# 在導入任何 LangChain 元件前就禁用追蹤以避免 TypeError
os.environ["LANGCHAIN_TRACING_V2"] = "false"
os.environ["LANGCHAIN_TRACING"] = "false"

from typing import Dict, Any
from logger import setup_logger
from langchain_core.messages import HumanMessage

from load_cfg import OPENAI_API_KEY, LANGCHAIN_API_KEY, WORKING_DIRECTORY
from core.workflow import WorkflowManager
from core.language_models import LanguageModelManager

class MultiAgentSystem:
    def __init__(self):
        self.logger = setup_logger()
        self.setup_environment()
        # Initialize the LanguageModelManager (reads config internally)
        self.lm_manager = LanguageModelManager()
        # Pass the manager instance to WorkflowManager
        self.workflow_manager = WorkflowManager(
            model_manager=self.lm_manager, # Pass the manager instance
            working_directory=WORKING_DIRECTORY
        )

    def setup_environment(self):
        """Initialize environment variables"""
        os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
        os.environ["LANGCHAIN_API_KEY"] = LANGCHAIN_API_KEY
        
        # 禁用 LangChain 追蹤以避免 TypeError 問題
        os.environ["LANGCHAIN_TRACING_V2"] = "false"
        os.environ["LANGCHAIN_TRACING"] = "false"
        
        # 移除 LANGCHAIN_PROJECT 設定以確保追蹤完全禁用
        if "LANGCHAIN_PROJECT" in os.environ:
            del os.environ["LANGCHAIN_PROJECT"]
        
        # 添加診斷日誌確認追蹤已禁用
        self.logger.info("LangChain 追蹤已禁用以避免 TypeError 問題")
        self.logger.info(f"LANGCHAIN_TRACING_V2: {os.environ.get('LANGCHAIN_TRACING_V2')}")
        self.logger.info(f"LANGCHAIN_TRACING: {os.environ.get('LANGCHAIN_TRACING')}")

        if not os.path.exists(WORKING_DIRECTORY):
            os.makedirs(WORKING_DIRECTORY)
            self.logger.info(f"Created working directory: {WORKING_DIRECTORY}")

    def run(self, user_input: str) -> None:
        """Run the multi-agent system with user input"""
        graph = self.workflow_manager.get_graph()
        events = graph.stream(
            {
                "messages": [HumanMessage(content=user_input)],
                "hypothesis": "",
                "process_decision": "",
                "process": "",
                "visualization_state": "",
                "searcher_state": "",
                "code_state": "",
                "report_section": "",
                "quality_review": "",
                "needs_revision": False,
                "last_sender": "",
            },
            {"configurable": {"thread_id": "1"}, "recursion_limit": 3000},
            stream_mode="values",
            debug=False
        )
        
        for event in events:
            message = event["messages"][-1]
            if isinstance(message, tuple):
                # 診斷日誌：記錄 tuple 訊息的詳細資訊
                logger.warning(f"⚠️  發現 tuple 訊息 - 類型: {type(message)}, 內容: {message}")
                logger.warning(f"⚠️  事件詳情: {event}")
                print(message, end='', flush=True)
            else:
                message.pretty_print()

def main():
    """Main entry point"""
    system = MultiAgentSystem()
    
    # Example usage
    user_input = '''
    datapath:OnlineSalesData.csv
    Use machine learning to perform data analysis and write complete graphical reports
    '''
    system.run(user_input)

if __name__ == "__main__":
    main()
