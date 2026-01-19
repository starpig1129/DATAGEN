"""WebSocket 管理器模組。"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime
from dataclasses import dataclass, asdict
from queue import Queue
from typing import Set, Dict, Any, Optional, Union

import websockets
from websockets.legacy.server import WebSocketServerProtocol

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class WebSocketMessage:
    """WebSocket 消息結構。"""
    id: str
    type: str
    data: Dict[str, Any]
    timestamp: int
    source: str = "server"


class WebSocketManager:
    """WebSocket 連接管理器。"""

    def __init__(self):
        self.connections: Set[Union[WebSocketServerProtocol, Any]] = set()
        self.client_info: Dict[Union[WebSocketServerProtocol, Any], Dict[str, Any]] = {}
        self.message_queue = Queue()
        self.running = False

    async def register(self, websocket: Union[WebSocketServerProtocol, Any], client_data: Optional[Dict[str, Any]] = None):
        """註冊新的 WebSocket 連接。"""
        self.connections.add(websocket)
        self.client_info[websocket] = client_data or {}

        client_addr = getattr(websocket, 'remote_address', getattr(websocket, 'client', 'unknown'))
        logger.info(f"新客戶端連接: {client_addr}, 總連接數: {len(self.connections)}")

        # 發送歡迎消息
        welcome_msg = WebSocketMessage(
            id=str(uuid.uuid4()),
            type="connection_established",
            data={
                "message": "WebSocket 連接已建立",
                "server_time": datetime.now().isoformat(),
                "client_id": self.client_info[websocket].get("clientId", "unknown")
            },
            timestamp=int(time.time() * 1000)
        )

        await self.send_to_client(websocket, welcome_msg)

        # 發送系統狀態
        await self.send_system_status(websocket)

    async def unregister(self, websocket: Union[WebSocketServerProtocol, Any]):
        """註銷 WebSocket 連接。"""
        self.connections.discard(websocket)
        if websocket in self.client_info:
            del self.client_info[websocket]

        client_addr = getattr(websocket, 'remote_address', getattr(websocket, 'client', 'unknown'))
        logger.info(f"客戶端斷開連接: {client_addr}, 剩餘連接數: {len(self.connections)}")

    async def send_to_client(self, websocket: Union[WebSocketServerProtocol, Any], message: WebSocketMessage):
        """向特定客戶端發送消息。"""
        try:
            message_json = json.dumps(asdict(message), ensure_ascii=False)
            # 檢查 WebSocket 類型並使用適當的方法
            if hasattr(websocket, 'send_text'):
                # FastAPI WebSocket
                await websocket.send_text(message_json)  # type: ignore
            else:
                # websockets WebSocket
                await websocket.send(message_json)
            logger.debug(f"消息已發送到 {getattr(websocket, 'remote_address', getattr(websocket, 'client', 'unknown'))}: {message.type}")
        except Exception as e:
            logger.error(f"發送消息失敗 {getattr(websocket, 'remote_address', getattr(websocket, 'client', 'unknown'))}: {e}")
            await self.unregister(websocket)

    async def broadcast(self, message: WebSocketMessage, exclude: Optional[Union[WebSocketServerProtocol, Any]] = None):
        """廣播消息給所有連接的客戶端。"""
        if not self.connections:
            return

        disconnected = set()

        for websocket in self.connections.copy():
            if websocket == exclude:
                continue

            try:
                await self.send_to_client(websocket, message)
            except websockets.exceptions.ConnectionClosed:
                disconnected.add(websocket)
            except Exception as e:
                logger.error(f"廣播消息失敗 {websocket.remote_address}: {e}")
                disconnected.add(websocket)

        # 清理斷開的連接
        for websocket in disconnected:
            await self.unregister(websocket)

        if disconnected:
            logger.info(f"清理了 {len(disconnected)} 個斷開的連接")

    async def send_system_status(self, websocket: Optional[Union[WebSocketServerProtocol, Any]] = None):
        """發送系統狀態。"""
        status_msg = WebSocketMessage(
            id=str(uuid.uuid4()),
            type="system_metrics",
            data={
                # TODO: Replace with actual data from backend logic
                "cpu": 45.2,
                "memory": 67.8,
                "disk": 23.4,
                "activeConnections": len(self.connections),
                "queueSize": self.message_queue.qsize(),
                "lastUpdate": datetime.now().isoformat()
            },
            timestamp=int(time.time() * 1000)
        )

        if websocket:
            await self.send_to_client(websocket, status_msg)
        else:
            await self.broadcast(status_msg)

    async def send_agent_status(self, agent_id: str, status: str, progress: int = 0, task: Optional[str] = None):
        """發送代理狀態更新。"""
        agent_msg = WebSocketMessage(
            id=str(uuid.uuid4()),
            type="agent_status",
            data={
                "agentId": agent_id,
                "name": agent_id.replace("_", " ").title(),
                "status": status,  # idle, processing, error, completed
                "progress": progress,
                "lastActivity": datetime.now().isoformat(),
                "currentTask": task
            },
            timestamp=int(time.time() * 1000)
        )

        await self.broadcast(agent_msg)

    async def send_state_update(self, state: Dict[str, Any], websocket=None):
        """發送應用程式狀態更新 (matches frontend state_update handler).

        Args:
            state: Application state dict matching BackendState interface.
            websocket: Optional specific client, otherwise broadcast to all.
        """
        state_msg = WebSocketMessage(
            id=str(uuid.uuid4()),
            type="state_update",
            data=state,
            timestamp=int(time.time() * 1000)
        )

        if websocket:
            await self.send_to_client(websocket, state_msg)
        else:
            await self.broadcast(state_msg)

    async def send_data_update(self, data_type: str, data: Dict[str, Any]):
        """發送數據更新。"""
        data_msg = WebSocketMessage(
            id=str(uuid.uuid4()),
            type="data_update",
            data={
                "type": data_type,
                "payload": data,
                "timestamp": datetime.now().isoformat()
            },
            timestamp=int(time.time() * 1000)
        )

        await self.broadcast(data_msg)

    async def send_file_status(self, file_info: Dict[str, Any]):
        """發送文件狀態更新。"""
        file_msg = WebSocketMessage(
            id=str(uuid.uuid4()),
            type="file_status",
            data=file_info,
            timestamp=int(time.time() * 1000)
        )

        await self.broadcast(file_msg)

    async def send_agent_message(
        self,
        agent_name: str,
        content: str,
        message_type: str = "text",
        websocket=None
    ):
        """發送 AI 代理訊息至前端。

        Args:
            agent_name: 代理名稱 (例如 "hypothesis_agent")
            content: 訊息文本內容
            message_type: 訊息類型 ("text", "hypothesis", "report" 等)
            websocket: 可選，指定發送到特定客戶端，否則廣播
        """
        agent_msg = WebSocketMessage(
            id=str(uuid.uuid4()),
            type="agent_message",
            data={
                "agentName": agent_name,
                "content": content,
                "messageType": message_type,
                "timestamp": datetime.now().isoformat()
            },
            timestamp=int(time.time() * 1000)
        )

        if websocket:
            await self.send_to_client(websocket, agent_msg)
        else:
            await self.broadcast(agent_msg)

    async def send_decision_required(
        self,
        prompt: str,
        options: list,
        decision_id: str = None,
        websocket=None
    ):
        """發送需要用戶決策的選項至前端。

        Args:
            prompt: 決策提示文字
            options: 選項列表 (例如 [{"id": "1", "label": "重新生成"}, ...])
            decision_id: 決策識別碼，用於追蹤回應
            websocket: 可選，指定發送到特定客戶端，否則廣播
        """
        if decision_id is None:
            decision_id = str(uuid.uuid4())

        decision_msg = WebSocketMessage(
            id=str(uuid.uuid4()),
            type="decision_required",
            data={
                "decisionId": decision_id,
                "prompt": prompt,
                "options": options,
                "timestamp": datetime.now().isoformat()
            },
            timestamp=int(time.time() * 1000)
        )

        if websocket:
            await self.send_to_client(websocket, decision_msg)
        else:
            await self.broadcast(decision_msg)

    async def send_chart_data(self, chart_id: str, chart_data: Dict[str, Any]):
        """發送圖表數據更新。"""
        chart_msg = WebSocketMessage(
            id=str(uuid.uuid4()),
            type="chart_data",
            data={
                "chartId": chart_id,
                "data": chart_data,
                "timestamp": datetime.now().isoformat()
            },
            timestamp=int(time.time() * 1000)
        )

        await self.broadcast(chart_msg)

    def start_background_tasks(self):
        """啟動背景任務。"""
        self.running = True
        logger.info("背景任務已啟動")

        # 注意：背景任務現在將在主事件循環中作為任務運行
        # 而不是在獨立的線程中，以避免跨線程事件循環問題

    async def run_background_tasks(self):
        """在主事件循環中運行背景任務。"""
        async def send_periodic_metrics():
            while self.running:
                try:
                    if self.connections:  # 只有在有連接時才發送
                        await self.send_system_status()
                    await asyncio.sleep(30)  # 每30秒發送一次系統狀態
                except Exception as e:
                    logger.error(f"定期發送系統指標失敗: {e}")
                    await asyncio.sleep(5)

        # 創建背景任務
        task = asyncio.create_task(send_periodic_metrics())
        return task

    def stop_background_tasks(self):
        """停止背景任務。"""
        self.running = False
        logger.info("背景任務已停止")


# 全域 WebSocket 管理器實例
ws_manager = WebSocketManager()


# WebSocket 管理器的公共 API
def broadcast_agent_update(agent_id: str, status: str, progress: int = 0, task: Optional[str] = None):
    """廣播代理狀態更新 (同步版本)。"""
    if ws_manager.connections:
        try:
            loop = asyncio.get_running_loop()
            # 如果在已有事件循環中，使用 create_task
            loop.create_task(ws_manager.send_agent_status(agent_id, status, progress, task))
        except RuntimeError:
            # 沒有運行的事件循環，創建新的
            asyncio.run(ws_manager.send_agent_status(agent_id, status, progress, task))


def broadcast_data_update(data_type: str, data: Dict[str, Any]):
    """廣播數據更新 (同步版本)。"""
    if ws_manager.connections:
        try:
            loop = asyncio.get_running_loop()
            # 如果在已有事件循環中，使用 create_task
            loop.create_task(ws_manager.send_data_update(data_type, data))
        except RuntimeError:
            # 沒有運行的事件循環，創建新的
            asyncio.run(ws_manager.send_data_update(data_type, data))


def broadcast_file_update(file_info: Dict[str, Any]):
    """廣播文件狀態更新 (同步版本)。"""
    if ws_manager.connections:
        try:
            loop = asyncio.get_running_loop()
            # 如果在已有事件循環中，使用 create_task
            loop.create_task(ws_manager.send_file_status(file_info))
        except RuntimeError:
            # 沒有運行的事件循環，創建新的
            asyncio.run(ws_manager.send_file_status(file_info))


def broadcast_chart_update(chart_id: str, chart_data: Dict[str, Any]):
    """廣播圖表數據更新 (同步版本)。"""
    if ws_manager.connections:
        try:
            loop = asyncio.get_running_loop()
            # 如果在已有事件循環中，使用 create_task
            loop.create_task(ws_manager.send_chart_data(chart_id, chart_data))
        except RuntimeError:
            # 沒有運行的事件循環，創建新的
            asyncio.run(ws_manager.send_chart_data(chart_id, chart_data))