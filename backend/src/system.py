import os
from typing import Dict, Any
from . import config, logger
from langchain_core.messages import HumanMessage

from .core import WorkflowManager, LanguageModelManager
from ..websocket_server import broadcast_agent_update

class MultiAgentSystem:
    def __init__(self):
        self.logger = logger.setup_logger()
        self.setup_environment()
        self.lm_manager = LanguageModelManager()
        self.workflow_manager = WorkflowManager(
            lm_manager=self.lm_manager,
            working_directory=config.WORKING_DIRECTORY
        )

    def setup_environment(self):
        """Initialize environment variables"""
        os.environ["OPENAI_API_KEY"] = config.OPENAI_API_KEY
        os.environ["LANGCHAIN_API_KEY"] = config.LANGCHAIN_API_KEY
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_PROJECT"] = "Multi-Agent Data Analysis System"

        if not os.path.exists(config.WORKING_DIRECTORY):
            os.makedirs(config.WORKING_DIRECTORY)
            self.logger.info(f"Created working directory: {config.WORKING_DIRECTORY}")

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
            # 廣播代理狀態更新
            sender = event.get("sender", "")
            if sender and sender != "human":
                # 將代理名稱轉換為更友好的格式
                agent_name = sender.replace("_agent", "").replace("_", " ").title()
                if agent_name == "Searcher":
                    agent_name = "Search"

                # 確定代理狀態和進度
                status = "processing"
                progress = 0
                task_description = f"{agent_name} 正在處理任務"

                # 根據代理類型提供更詳細的描述
                if "hypothesis" in sender:
                    task_description = "正在生成研究假設"
                    progress = 20
                elif "process" in sender:
                    task_description = "正在規劃研究流程"
                    progress = 30
                elif "searcher" in sender:
                    task_description = "正在搜尋相關文獻"
                    progress = 40
                elif "code" in sender:
                    task_description = "正在編寫程式碼"
                    progress = 50
                elif "visualization" in sender:
                    task_description = "正在建立視覺化"
                    progress = 60
                elif "report" in sender:
                    task_description = "正在生成報告"
                    progress = 70
                elif "quality" in sender:
                    task_description = "正在進行品質審查"
                    progress = 80
                elif "note" in sender:
                    task_description = "正在記錄筆記"
                    progress = 15
                elif "refiner" in sender:
                    task_description = "正在優化結果"
                    progress = 90

                # 檢查狀態信息來調整進度和描述
                if event.get("hypothesis"):
                    task_description = "研究假設已生成"
                    progress = 25
                if event.get("process"):
                    task_description = "研究流程已規劃"
                    progress = 35
                if event.get("searcher_state"):
                    task_description = "文獻搜尋完成"
                    progress = 45
                if event.get("code_state"):
                    task_description = "程式碼編寫完成"
                    progress = 55
                if event.get("visualization_state"):
                    task_description = "視覺化建立完成"
                    progress = 65
                if event.get("report_section"):
                    task_description = "報告生成完成"
                    progress = 75
                if event.get("quality_review"):
                    task_description = "品質審查完成"
                    progress = 85
                if event.get("needs_revision", False):
                    status = "revision_required"
                    task_description = "需要修改和優化"
                    progress = 10

                # 呼叫 WebSocket 廣播
                broadcast_agent_update(agent_name.lower().replace(" ", "_"), status, progress, task_description)

            message = event["messages"][-1]
            if isinstance(message, tuple):
                print(message, end='', flush=True)
            else:
                message.pretty_print()