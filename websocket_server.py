import asyncio
import json
import logging
import websockets
from websockets.legacy.server import WebSocketServerProtocol
from typing import Set, Dict, Any
from datetime import datetime
import threading
import time
from dataclasses import dataclass, asdict
from queue import Queue
import uuid

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class WebSocketMessage:
    """WebSocket 消息結構"""
    id: str
    type: str
    data: Dict[str, Any]
    timestamp: int
    source: str = "server"

class WebSocketManager:
    """WebSocket 連接管理器"""
    
    def __init__(self):
        self.connections: Set[WebSocketServerProtocol] = set()
        self.client_info: Dict[WebSocketServerProtocol, Dict[str, Any]] = {}
        self.message_queue = Queue()
        self.running = False
        
    async def register(self, websocket: WebSocketServerProtocol, client_data: Dict[str, Any] = None):
        """註冊新的 WebSocket 連接"""
        self.connections.add(websocket)
        self.client_info[websocket] = client_data or {}
        
        logger.info(f"新客戶端連接: {websocket.remote_address}, 總連接數: {len(self.connections)}")
        
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

    async def unregister(self, websocket: WebSocketServerProtocol):
        """註銷 WebSocket 連接"""
        self.connections.discard(websocket)
        if websocket in self.client_info:
            del self.client_info[websocket]
            
        logger.info(f"客戶端斷開連接: {websocket.remote_address}, 剩餘連接數: {len(self.connections)}")

    async def send_to_client(self, websocket: WebSocketServerProtocol, message: WebSocketMessage):
        """向特定客戶端發送消息"""
        try:
            message_json = json.dumps(asdict(message), ensure_ascii=False)
            await websocket.send(message_json)
            logger.debug(f"消息已發送到 {websocket.remote_address}: {message.type}")
        except websockets.exceptions.ConnectionClosed:
            logger.warning(f"嘗試向已關閉的連接發送消息: {websocket.remote_address}")
            await self.unregister(websocket)
        except Exception as e:
            logger.error(f"發送消息失敗 {websocket.remote_address}: {e}")

    async def broadcast(self, message: WebSocketMessage, exclude: WebSocketServerProtocol = None):
        """廣播消息給所有連接的客戶端"""
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

    async def send_system_status(self, websocket: WebSocketServerProtocol = None):
        """發送系統狀態"""
        status_msg = WebSocketMessage(
            id=str(uuid.uuid4()),
            type="system_metrics",
            data={
                "cpu": 45.2,  # 模擬 CPU 使用率
                "memory": 67.8,  # 模擬內存使用率
                "disk": 23.4,  # 模擬磁盤使用率
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

    async def send_agent_status(self, agent_id: str, status: str, progress: int = 0, task: str = None):
        """發送代理狀態更新"""
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

    async def send_data_update(self, data_type: str, data: Dict[str, Any]):
        """發送數據更新"""
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
        """發送文件狀態更新"""
        file_msg = WebSocketMessage(
            id=str(uuid.uuid4()),
            type="file_status",
            data=file_info,
            timestamp=int(time.time() * 1000)
        )
        
        await self.broadcast(file_msg)

    async def send_chart_data(self, chart_id: str, chart_data: Dict[str, Any]):
        """發送圖表數據更新"""
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
        """啟動背景任務"""
        self.running = True
        logger.info("背景任務已啟動")
        
        # 注意：背景任務現在將在主事件循環中作為任務運行
        # 而不是在獨立的線程中，以避免跨線程事件循環問題
    
    async def run_background_tasks(self):
        """在主事件循環中運行背景任務"""
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
        """停止背景任務"""
        self.running = False
        logger.info("背景任務已停止")

# 全域 WebSocket 管理器實例
ws_manager = WebSocketManager()

async def handle_websocket(websocket: WebSocketServerProtocol):
    """處理 WebSocket 連接"""
    try:
        # 等待客戶端初始化消息
        init_message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
        
        try:
            init_data = json.loads(init_message)
            logger.info(f"收到初始化消息: {init_data}")
        except json.JSONDecodeError:
            init_data = {"type": "init", "clientId": "unknown"}
        
        # 註冊客戶端
        await ws_manager.register(websocket, init_data)
        
        # 處理客戶端消息
        async for message in websocket:
            try:
                data = json.loads(message)
                await handle_client_message(websocket, data)
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
        logger.warning(f"客戶端初始化超時: {websocket.remote_address}")
    except websockets.exceptions.ConnectionClosed:
        logger.info(f"客戶端連接已關閉: {websocket.remote_address}")
    except Exception as e:
        logger.error(f"WebSocket 處理錯誤: {e}")
    finally:
        await ws_manager.unregister(websocket)

async def handle_client_message(websocket: WebSocketServerProtocol, data: Dict[str, Any]):
    """處理客戶端發送的消息"""
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
            # 發送模擬代理狀態
            await ws_manager.send_agent_status("search_agent", "processing", 45, "搜尋相關文獻")
            await ws_manager.send_agent_status("analysis_agent", "idle", 0)
            
        if subscription_type in ["all", "data_update"]:
            # 發送模擬數據更新
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
            # 發送模擬圖表數據
            await ws_manager.send_chart_data("performance_chart", {
                "labels": ["Mon", "Tue", "Wed", "Thu", "Fri"],
                "datasets": [{
                    "label": "Performance",
                    "data": [12, 19, 15, 17, 14]
                }]
            })
            
    else:
        logger.warning(f"未知消息類型: {message_type}")

def start_websocket_server(host: str = "localhost", port: int = 8765):
    """啟動 WebSocket 伺服器"""
    logger.info(f"啟動 WebSocket 伺服器 ws://{host}:{port}")
    
    async def main():
        """主要的異步運行函數"""
        # 啟動背景任務
        ws_manager.start_background_tasks()
        
        # 啟動伺服器
        start_server = websockets.serve(handle_websocket, host, port)
        server = await start_server
        
        logger.info(f"WebSocket 伺服器已啟動在 ws://{host}:{port}")
        
        # 啟動背景任務
        background_task = await ws_manager.run_background_tasks()
        
        try:
            # 運行直到收到中斷信號
            await server.wait_closed()
        except asyncio.CancelledError:
            logger.info("WebSocket 伺服器被取消")
        finally:
            # 取消背景任務
            if background_task and not background_task.done():
                background_task.cancel()
                try:
                    await background_task
                except asyncio.CancelledError:
                    pass
            ws_manager.stop_background_tasks()
            logger.info("WebSocket 伺服器已關閉")
    
    try:
        # 使用 asyncio.run() 來確保正確的事件循環管理
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("收到中斷信號，正在關閉伺服器...")
    except Exception as e:
        logger.error(f"WebSocket 伺服器啟動失敗: {e}")
        raise

# WebSocket 管理器的公共 API
def broadcast_agent_update(agent_id: str, status: str, progress: int = 0, task: str = None):
    """廣播代理狀態更新 (同步版本)"""
    if ws_manager.connections:
        try:
            loop = asyncio.get_running_loop()
            # 如果在已有事件循環中，使用 create_task
            loop.create_task(ws_manager.send_agent_status(agent_id, status, progress, task))
        except RuntimeError:
            # 沒有運行的事件循環，創建新的
            asyncio.run(ws_manager.send_agent_status(agent_id, status, progress, task))

def broadcast_data_update(data_type: str, data: Dict[str, Any]):
    """廣播數據更新 (同步版本)"""
    if ws_manager.connections:
        try:
            loop = asyncio.get_running_loop()
            # 如果在已有事件循環中，使用 create_task
            loop.create_task(ws_manager.send_data_update(data_type, data))
        except RuntimeError:
            # 沒有運行的事件循環，創建新的
            asyncio.run(ws_manager.send_data_update(data_type, data))

def broadcast_file_update(file_info: Dict[str, Any]):
    """廣播文件狀態更新 (同步版本)"""
    if ws_manager.connections:
        try:
            loop = asyncio.get_running_loop()
            # 如果在已有事件循環中，使用 create_task
            loop.create_task(ws_manager.send_file_status(file_info))
        except RuntimeError:
            # 沒有運行的事件循環，創建新的
            asyncio.run(ws_manager.send_file_status(file_info))

def broadcast_chart_update(chart_id: str, chart_data: Dict[str, Any]):
    """廣播圖表數據更新 (同步版本)"""
    if ws_manager.connections:
        try:
            loop = asyncio.get_running_loop()
            # 如果在已有事件循環中，使用 create_task
            loop.create_task(ws_manager.send_chart_data(chart_id, chart_data))
        except RuntimeError:
            # 沒有運行的事件循環，創建新的
            asyncio.run(ws_manager.send_chart_data(chart_id, chart_data))

if __name__ == "__main__":
    # 如果直接運行此檔案，啟動 WebSocket 伺服器
    import argparse
    
    parser = argparse.ArgumentParser(description="WebSocket 實時更新伺服器")
    parser.add_argument("--host", default="localhost", help="伺服器主機地址")
    parser.add_argument("--port", type=int, default=8765, help="伺服器端口")
    
    args = parser.parse_args()
    
    start_websocket_server(args.host, args.port)