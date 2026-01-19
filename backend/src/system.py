import os
import sys
from typing import Dict, Any
from pathlib import Path

# 調整路徑以支援模組導入
backend_path = str(Path(__file__).resolve().parent.parent)
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from config.settings import (
    OPENAI_API_KEY,
    LANGCHAIN_API_KEY,
    WORKING_DIRECTORY,
    AGENT_MODELS
)
from . import logger
from langchain_core.messages import HumanMessage, AIMessage

from .core import WorkflowManager, LanguageModelManager
from websocket_server import broadcast_agent_update
from core.services.system_service import SystemService

class MultiAgentSystem:
    def __init__(self):
        self.logger = logger.setup_logger()
        self.setup_environment()
        self.lm_manager = LanguageModelManager()
        self.workflow_manager = WorkflowManager(
            lm_manager=self.lm_manager,
            working_directory=WORKING_DIRECTORY
        )

    def get_agent_models(self):
        """取得代理模型組態。"""
        return AGENT_MODELS

    def setup_environment(self):
        """Initialize environment variables"""
        os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
        os.environ["LANGCHAIN_API_KEY"] = LANGCHAIN_API_KEY
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_PROJECT"] = "Multi-Agent Data Analysis System"

        if not os.path.exists(WORKING_DIRECTORY):
            os.makedirs(WORKING_DIRECTORY)
            self.logger.info(f"Created working directory: {WORKING_DIRECTORY}")

    def run(self, user_input: str, websocket_callback=None) -> None:
        """Run the multi-agent system with user input

        Args:
            user_input: The user's input for analysis
            websocket_callback: Optional callback function for WebSocket broadcasting.
                If provided, it should accept (msg_type: str, **kwargs) where msg_type is:
                - "status": agent_id, status, progress, task
                - "message": agent_name, content, message_type
                - "decision": prompt, options
                - "state_update": state (full application state dict)
                If not provided (CLI mode), output goes to stdout via print/pretty_print.
        """
        # Clear previous state for new analysis
        SystemService.clear_state()
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

                # 根據 websocket_callback 的存在決定輸出方式
                if websocket_callback:
                    # 通過 WebSocket 廣播代理狀態
                    websocket_callback(
                        "status",
                        agent_id=agent_name.lower().replace(" ", "_"),
                        status=status,
                        progress=progress,
                        task=task_description
                    )
                else:
                    # 直接呼叫 WebSocket 廣播（保持向後兼容性）
                    broadcast_agent_update(agent_name.lower().replace(" ", "_"), status, progress, task_description)

            # 處理訊息輸出
            message = event["messages"][-1]
            
            # 只推播 AI 訊息，跳過 HumanMessage
            is_ai_message = isinstance(message, AIMessage) or (hasattr(message, 'type') and message.type == 'ai')
            
            # Check if workflow requires human decision (from LangGraph state)
            needs_decision = event.get("needs_decision", False) or sender in ["human_choice", "human_review"]
            
            if isinstance(message, tuple):
                content = str(message)
                if websocket_callback and is_ai_message:
                    # Update state with new message
                    msg_dict = {"content": content, "type": "assistant", "sender": sender or "assistant"}
                    new_state = SystemService.update_state(
                        sender=sender,
                        message=msg_dict,
                        needs_decision=needs_decision
                    )
                    websocket_callback("message", agent_name=sender, content=content, message_type="text")
                    # Broadcast full state update
                    websocket_callback("state_update", state=new_state)
                print(content, end='', flush=True)
            else:
                # 獲取訊息內容
                content = getattr(message, 'content', str(message))
                agent_name = getattr(message, 'name', sender or 'assistant')
                
                # 透過 WebSocket 推播 AI 訊息 (若有 callback)，跳過 HumanMessage
                if websocket_callback and content and is_ai_message:
                    # 判斷訊息類型 (安全處理 agent_name 可能為 None 的情況)
                    message_type = "text"
                    agent_name_lower = (agent_name or "").lower()
                    if "hypothesis" in agent_name_lower:
                        message_type = "hypothesis"
                    elif "report" in agent_name_lower:
                        message_type = "report"
                    
                    # Update application state
                    msg_dict = {"content": content, "type": "assistant", "sender": agent_name or "assistant"}
                    new_state = SystemService.update_state(
                        sender=sender,
                        message=msg_dict,
                        needs_decision=needs_decision,
                        hypothesis=event.get("hypothesis", ""),
                        process=event.get("process", ""),
                        visualization_state=event.get("visualization_state", ""),
                        code_state=event.get("code_state", ""),
                        report_section=event.get("report_section", ""),
                        quality_review=event.get("quality_review", ""),
                        needs_revision=event.get("needs_revision", False)
                    )
                    
                    websocket_callback("message", agent_name=agent_name, content=content, message_type=message_type)
                    
                    # Broadcast full state update for frontend sync
                    websocket_callback("state_update", state=new_state)
                
                # CLI 模式保留原行為
                message.pretty_print()
        
        # After stream ends, check if we're paused at an interrupt point (HumanChoice/HumanReview)
        if websocket_callback:
            config = {"configurable": {"thread_id": "1"}}
            graph_state = graph.get_state(config)
            
            # Check if there are next nodes waiting (indicates we're at an interrupt)
            if graph_state.next:
                next_nodes = list(graph_state.next)
                self.logger.info(f"Workflow paused at: {next_nodes}")
                
                if "HumanChoice" in next_nodes or "HumanReview" in next_nodes:
                    # Signal frontend that decision is needed
                    new_state = SystemService.update_state(
                        sender="human_choice",
                        needs_decision=True
                    )
                    
                    # Determine prompt and options based on which node
                    if "HumanChoice" in next_nodes:
                        prompt = "請選擇下一步操作："
                        options = [
                            {"id": "1", "label": "重新生成假設", "value": "1"},
                            {"id": "2", "label": "繼續研究流程", "value": "2"}
                        ]
                    else:  # HumanReview
                        prompt = "是否需要額外分析或修改？"
                        options = [
                            {"id": "yes", "label": "是，繼續分析", "value": "yes"},
                            {"id": "no", "label": "否，結束研究", "value": "no"}
                        ]
                    
                    websocket_callback("state_update", state=new_state)
                    websocket_callback("decision", prompt=prompt, options=options)
                    self.logger.info("Decision required signal sent to frontend")