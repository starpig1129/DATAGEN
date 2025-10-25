"""根級別的 API 路由（無 prefix）。"""

import json
import asyncio
import logging
import time
import uuid
from datetime import datetime

from fastapi import APIRouter, WebSocket

# 導入 WebSocket 相關
from websocket_server.manager import ws_manager, WebSocketMessage
from websocket_server.handlers.client import handle_client_message_fastapi

# 建立路由器
router = APIRouter()

# 配置日誌
logger = logging.getLogger(__name__)


@router.websocket("/stream")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket 端點"""
    try:
        # 等待客戶端初始化消息
        init_message = await asyncio.wait_for(websocket.receive_text(), timeout=10.0)

        try:
            init_data = json.loads(init_message)
            logger.info(f"收到初始化消息: {init_data}")
        except json.JSONDecodeError:
            init_data = {"type": "init", "clientId": "unknown"}

        # 註冊客戶端
        await ws_manager.register(websocket, init_data)

        # 發送歡迎消息
        welcome_msg = WebSocketMessage(
            id=str(uuid.uuid4()),
            type="connection_established",
            data={
                "message": "WebSocket 連接已建立",
                "server_time": datetime.now().isoformat(),
                "client_id": init_data.get("clientId", "unknown")
            },
            timestamp=int(time.time() * 1000)
        )
        await ws_manager.send_to_client(websocket, welcome_msg)

        # 發送系統狀態
        await ws_manager.send_system_status(websocket)

        # 處理客戶端消息
        while True:
            try:
                message = await websocket.receive_text()
                data = json.loads(message)
                await handle_client_message_fastapi(websocket, data)
            except json.JSONDecodeError as e:
                logger.error(f"JSON 解析錯誤: {e}")
                error_msg = WebSocketMessage(
                    id=str(uuid.uuid4()),
                    type="error",
                    data={"message": "無效的 JSON 格式"},
                    timestamp=int(time.time() * 1000)
                )
                await ws_manager.send_to_client(websocket, error_msg)
            except Exception as e:
                logger.error(f"處理客戶端消息失敗: {e}")

    except asyncio.TimeoutError:
        logger.warning(f"客戶端初始化超時: {getattr(websocket, 'client', 'unknown')}")
    except Exception as e:
        logger.error(f"FastAPI WebSocket 處理錯誤: {e}")
    finally:
        await ws_manager.unregister(websocket)


@router.get("/health")
async def health_check():
    """健康檢查端點"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@router.get("/")
async def root():
    """根端點"""
    return {
        "message": "多代理數據分析系統 API",
        "version": "1.0.0",
        "docs": "/docs"
    }