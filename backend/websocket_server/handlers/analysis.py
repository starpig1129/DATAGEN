"""WebSocket 分析任務處理器模組。"""

import asyncio
import logging
import time
import uuid
from datetime import datetime
from typing import Dict, Any

from ..manager import WebSocketMessage, ws_manager

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def run_analysis_async(websocket, user_input: str):
    """異步運行分析任務 (原始 websockets 版本)。"""
    try:
        # 延遲導入 MultiAgentSystem 以避免循環導入
        import sys
        import os
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
        from src.system import MultiAgentSystem

        # 建立 MultiAgentSystem 實例
        system = MultiAgentSystem()

        # 定義 WebSocket 回調函數
        def websocket_callback(agent_id: str, status: str, progress: int, task: str):
            """WebSocket 回調函數，用於廣播代理狀態更新。"""
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(ws_manager.send_agent_status(agent_id, status, progress, task))
            except RuntimeError:
                # 沒有運行的事件循環，創建新的
                asyncio.run(ws_manager.send_agent_status(agent_id, status, progress, task))

        # 運行分析
        system.run(user_input, websocket_callback=websocket_callback)

        # 發送分析完成消息
        completion_msg = WebSocketMessage(
            id=str(uuid.uuid4()),
            type="analysis_completed",
            data={
                "message": "分析已完成",
                "timestamp": datetime.now().isoformat()
            },
            timestamp=int(time.time() * 1000)
        )
        await ws_manager.send_to_client(websocket, completion_msg)

    except Exception as e:
        logger.error(f"分析任務失敗: {e}")
        # 發送錯誤消息
        error_msg = WebSocketMessage(
            id=str(uuid.uuid4()),
            type="analysis_error",
            data={
                "message": f"分析失敗: {str(e)}",
                "timestamp": datetime.now().isoformat()
            },
            timestamp=int(time.time() * 1000)
        )
        await ws_manager.send_to_client(websocket, error_msg)


async def run_analysis_async_fastapi(websocket, user_input: str):
    """異步運行分析任務 (FastAPI 版本)。"""
    try:
        # 延遲導入 MultiAgentSystem 以避免循環導入
        import sys
        import os
        from concurrent.futures import ThreadPoolExecutor
        import queue
        
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
        from src.system import MultiAgentSystem

        # 建立 MultiAgentSystem 實例
        system = MultiAgentSystem()
        
        # 使用 Queue 來跨線程傳遞訊息
        message_queue = queue.Queue()
        analysis_done = False

        # 定義 WebSocket 回調函數 (支援多種訊息類型)
        def websocket_callback(msg_type: str, **kwargs):
            """WebSocket 回調函數，將訊息放入隊列等待發送。"""
            message_queue.put((msg_type, kwargs))

        # 在背景線程執行分析
        def run_analysis():
            nonlocal analysis_done
            try:
                system.run(user_input, websocket_callback=websocket_callback)
            finally:
                analysis_done = True
                message_queue.put(("_done", {}))
        
        # 使用 executor 在背景線程運行
        loop = asyncio.get_running_loop()
        executor = ThreadPoolExecutor(max_workers=1)
        analysis_task = loop.run_in_executor(executor, run_analysis)
        
        # 持續處理訊息隊列直到分析完成
        while True:
            try:
                # 非阻塞地檢查隊列
                try:
                    msg_type, kwargs = message_queue.get_nowait()
                except queue.Empty:
                    # 隊列為空，讓出控制權
                    await asyncio.sleep(0.1)
                    if analysis_done and message_queue.empty():
                        break
                    continue
                
                if msg_type == "_done":
                    break
                    
                if msg_type == "status":
                    agent_id = kwargs.get("agent_id", "unknown")
                    status = kwargs.get("status", "processing")
                    progress = kwargs.get("progress", 0)
                    task = kwargs.get("task", "")
                    await ws_manager.send_agent_status(agent_id, status, progress, task)
                    
                elif msg_type == "message":
                    agent_name = kwargs.get("agent_name", "assistant")
                    content = kwargs.get("content", "")
                    message_type = kwargs.get("message_type", "text")
                    await ws_manager.send_agent_message(agent_name, content, message_type, websocket)
                    
                elif msg_type == "decision":
                    prompt = kwargs.get("prompt", "請選擇下一步")
                    options = kwargs.get("options", [])
                    await ws_manager.send_decision_required(prompt, options, websocket=websocket)
                    
            except Exception as e:
                logger.error(f"處理訊息時發生錯誤: {e}")
        
        # 等待分析任務完成
        await analysis_task
        executor.shutdown(wait=False)

        # 發送分析完成消息
        completion_msg = WebSocketMessage(
            id=str(uuid.uuid4()),
            type="analysis_completed",
            data={
                "message": "分析已完成",
                "timestamp": datetime.now().isoformat()
            },
            timestamp=int(time.time() * 1000)
        )
        await ws_manager.send_to_client(websocket, completion_msg)

    except Exception as e:
        logger.error(f"分析任務失敗: {e}")
        # 發送錯誤消息
        error_msg = WebSocketMessage(
            id=str(uuid.uuid4()),
            type="analysis_error",
            data={
                "message": f"分析失敗: {str(e)}",
                "timestamp": datetime.now().isoformat()
            },
            timestamp=int(time.time() * 1000)
        )
        await ws_manager.send_to_client(websocket, error_msg)