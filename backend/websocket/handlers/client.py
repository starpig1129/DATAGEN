"""WebSocket 客戶端消息處理器模組。"""

import json
import logging
import time
import uuid
from datetime import datetime
from typing import Dict, Any

from ..manager import WebSocketMessage, ws_manager

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def handle_client_message(websocket, data: Dict[str, Any]):
    """處理客戶端發送的消息 (原始 websockets 版本)。"""
    message_type = data.get("type", "unknown")

    logger.info(f"收到客戶端消息: {message_type} from {websocket.remote_address}")

    if message_type == "ping":
        # 回應 ping 消息
        pong_msg = WebSocketMessage(
            id=str(uuid.uuid4()),
            type="pong",
            data={"timestamp": datetime.now().isoformat()},
            timestamp=int(time.time() * 1000)
        )
        await ws_manager.send_to_client(websocket, pong_msg)

    elif message_type == "request_status":
        # 發送當前系統狀態
        await ws_manager.send_system_status(websocket)

    elif message_type == "subscribe":
        # 處理訂閱請求
        subscription_type = data.get("subscription", "all")
        logger.info(f"客戶端訂閱: {subscription_type}")

        # 根據訂閱類型發送相應數據
        if subscription_type in ["all", "agent_status"]:
            # TODO: Replace with actual data from backend logic
            await ws_manager.send_agent_status("search_agent", "processing", 45, "搜尋相關文獻")
            await ws_manager.send_agent_status("analysis_agent", "idle", 0)

        if subscription_type in ["all", "data_update"]:
            # TODO: Replace with actual data from backend logic
            await ws_manager.send_data_update("dashboard_metrics", {
                "totalFiles": 23,
                "totalAnalyses": 8,
                "activeAgents": 2,
                "lastUpdate": datetime.now().isoformat()
            })

    elif message_type == "trigger_update":
        # 手動觸發更新
        update_type = data.get("updateType", "all")
        logger.info(f"手動觸發更新: {update_type}")

        if update_type in ["all", "charts"]:
            # TODO: Replace with actual data from backend logic
            await ws_manager.send_chart_data("performance_chart", {
                "labels": ["Mon", "Tue", "Wed", "Thu", "Fri"],
                "datasets": [{
                    "label": "Performance",
                    "data": [12, 19, 15, 17, 14]
                }]
            })

    elif message_type == "start_analysis":
        # 處理分析請求
        user_input = data.get("userInput", "")
        if not user_input:
            error_msg = WebSocketMessage(
                id=str(uuid.uuid4()),
                type="error",
                data={"message": "缺少 userInput 參數"},
                timestamp=int(time.time() * 1000)
            )
            await ws_manager.send_to_client(websocket, error_msg)
            return

        logger.info(f"開始分析: {user_input[:50]}...")

        # 發送分析開始確認
        start_msg = WebSocketMessage(
            id=str(uuid.uuid4()),
            type="analysis_started",
            data={
                "message": "分析已開始",
                "userInput": user_input,
                "timestamp": datetime.now().isoformat()
            },
            timestamp=int(time.time() * 1000)
        )
        await ws_manager.send_to_client(websocket, start_msg)

        # 在新的異步任務中運行分析
        from .analysis import run_analysis_async
        import asyncio
        asyncio.create_task(run_analysis_async(websocket, user_input))

    else:
        logger.warning(f"未知消息類型: {message_type}")


async def handle_client_message_fastapi(websocket, data: Dict[str, Any]):
    """處理客戶端發送的消息 (FastAPI 版本)。"""
    message_type = data.get("type", "unknown")

    logger.info(f"收到客戶端消息: {message_type} from {getattr(websocket, 'client', 'unknown')}")

    if message_type == "ping":
        # 回應 ping 消息
        pong_msg = WebSocketMessage(
            id=str(uuid.uuid4()),
            type="pong",
            data={"timestamp": datetime.now().isoformat()},
            timestamp=int(time.time() * 1000)
        )
        await ws_manager.send_to_client(websocket, pong_msg)

    elif message_type == "request_status":
        # 發送當前系統狀態
        await ws_manager.send_system_status(websocket)

    elif message_type == "subscribe":
        # 處理訂閱請求
        subscription_type = data.get("subscription", "all")
        logger.info(f"客戶端訂閱: {subscription_type}")

        # 根據訂閱類型發送相應數據
        if subscription_type in ["all", "agent_status"]:
            # TODO: Replace with actual data from backend logic
            await ws_manager.send_agent_status("search_agent", "processing", 45, "搜尋相關文獻")
            await ws_manager.send_agent_status("analysis_agent", "idle", 0)

        if subscription_type in ["all", "data_update"]:
            # TODO: Replace with actual data from backend logic
            await ws_manager.send_data_update("dashboard_metrics", {
                "totalFiles": 23,
                "totalAnalyses": 8,
                "activeAgents": 2,
                "lastUpdate": datetime.now().isoformat()
            })

    elif message_type == "trigger_update":
        # 手動觸發更新
        update_type = data.get("updateType", "all")
        logger.info(f"手動觸發更新: {update_type}")

        if update_type in ["all", "charts"]:
            # TODO: Replace with actual data from backend logic
            await ws_manager.send_chart_data("performance_chart", {
                "labels": ["Mon", "Tue", "Wed", "Thu", "Fri"],
                "datasets": [{
                    "label": "Performance",
                    "data": [12, 19, 15, 17, 14]
                }]
            })

    elif message_type == "start_analysis":
        # 處理分析請求
        user_input = data.get("userInput", "")
        if not user_input:
            error_msg = WebSocketMessage(
                id=str(uuid.uuid4()),
                type="error",
                data={"message": "缺少 userInput 參數"},
                timestamp=int(time.time() * 1000)
            )
            await ws_manager.send_to_client(websocket, error_msg)
            return

        logger.info(f"開始分析: {user_input[:50]}...")

        # 發送分析開始確認
        start_msg = WebSocketMessage(
            id=str(uuid.uuid4()),
            type="analysis_started",
            data={
                "message": "分析已開始",
                "userInput": user_input,
                "timestamp": datetime.now().isoformat()
            },
            timestamp=int(time.time() * 1000)
        )
        await ws_manager.send_to_client(websocket, start_msg)

        # 在新的異步任務中運行分析
        from .analysis import run_analysis_async_fastapi
        import asyncio
        asyncio.create_task(run_analysis_async_fastapi(websocket, user_input))

    else:
        logger.warning(f"未知消息類型: {message_type}")