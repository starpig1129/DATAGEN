"""根級別的 API 路由（無 prefix）。"""

import json
import asyncio
import logging
import time
import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, WebSocket, HTTPException
from pydantic import BaseModel

# 導入 WebSocket 相關
from websocket_server.manager import ws_manager, WebSocketMessage
from websocket_server.handlers.client import handle_client_message_fastapi

# 建立路由器
router = APIRouter()

# 配置日誌
logger = logging.getLogger(__name__)


class SendMessageRequest(BaseModel):
    """Request model for sending a message."""
    message: str
    decision: Optional[str] = None


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


@router.post("/api/send_message")
async def send_message(request: SendMessageRequest):
    """HTTP endpoint to send a chat message.

    This provides an HTTP fallback when WebSocket is unavailable.
    The message is processed asynchronously and results are sent
    back via the WebSocket connection if available.

    Args:
        request: Message request containing the user message.

    Returns:
        Dict with message receipt confirmation.
    """
    try:
        message_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()

        logger.info(f"Received HTTP message: {request.message[:100]}...")

        # Check if this is a decision response
        if request.decision:
            logger.info(f"Processing decision: {request.decision}")
            # Broadcast decision to all connected clients
            decision_msg = WebSocketMessage(
                id=message_id,
                type="decision_received",
                data={
                    "decision": request.decision,
                    "timestamp": timestamp
                },
                timestamp=int(time.time() * 1000)
            )
            await ws_manager.broadcast(decision_msg)
            return {
                "status": "decision_received",
                "message_id": message_id,
                "decision": request.decision,
                "timestamp": timestamp
            }

        # For regular messages, trigger analysis via WebSocket broadcast
        # This allows connected clients to receive updates
        user_msg = WebSocketMessage(
            id=message_id,
            type="user_message_received",
            data={
                "message": request.message,
                "timestamp": timestamp,
                "source": "http_api"
            },
            timestamp=int(time.time() * 1000)
        )
        await ws_manager.broadcast(user_msg)

        # Also trigger the analysis workflow
        analysis_data = {
            "type": "start_analysis",
            "userInput": request.message
        }

        # Start analysis in background (broadcast to first connected client)
        clients = list(ws_manager.connections)
        if clients:
            # We need to ensure we're passing a valid websocket object
            # capable of sending responses if handle_client_message_fastapi expects one
            await handle_client_message_fastapi(clients[0], analysis_data)
        else:
            logger.warning("No active WebSocket connections to process message")

        return {
            "status": "message_received",
            "message_id": message_id,
            "message": request.message,
            "timestamp": timestamp,
            "note": "Processing will be delivered via WebSocket"
        }

    except Exception as e:
        logger.error(f"Failed to process message: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process message: {str(e)}"
        )