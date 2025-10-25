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