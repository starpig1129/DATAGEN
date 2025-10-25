"""應用程式主入口。"""

import os
import json
import asyncio
import logging
import time
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, WebSocket
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel

# 導入系統組件
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.factory import create_app
from src.system import MultiAgentSystem
from websocket.manager import ws_manager, WebSocketMessage
from websocket.handlers.client import handle_client_message_fastapi
from core.services.file_service import FileService
from core.services.system_service import SystemService
from core.services.analysis_service import AnalysisService

# 建立應用程式實例
app = create_app()

# 初始化服務層
file_service = FileService()
system_service = SystemService(ws_manager)
analysis_service = AnalysisService(ws_manager)

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 請求/響應模型
class SystemStatusResponse(BaseModel):
    """系統狀態響應"""
    status: str
    timestamp: str
    version: str
    websocket_connections: int
    system_info: Dict[str, Any]

class FileContentResponse(BaseModel):
    """文件內容響應"""
    content: str
    encoding: str
    size: int
    last_modified: str

class AnalysisRequest(BaseModel):
    """分析請求"""
    user_input: str
    options: Optional[Dict[str, Any]] = None

class AnalysisResponse(BaseModel):
    """分析響應"""
    analysis_id: str
    status: str
    message: str
    timestamp: str

class SettingsRequest(BaseModel):
    """設定請求"""
    settings: Dict[str, Any]

# API 路由

@app.websocket("/stream")
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

@app.get("/api/system/status", response_model=SystemStatusResponse)
async def get_system_status():
    """獲取系統狀態"""
    try:
        system_status = system_service.get_system_status()
        return SystemStatusResponse(**system_status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取系統狀態失敗: {str(e)}")

@app.get("/api/state")
async def get_state():
    """獲取應用程式狀態"""
    return system_service.get_state()

@app.get("/api/files/content/{file_path:path}", response_model=FileContentResponse)
async def get_file_content(file_path: str):
    """獲取文件內容"""
    try:
        file_data = file_service.get_file_content(file_path)
        return FileContentResponse(**file_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"讀取文件失敗: {str(e)}")

@app.get("/api/files/list/{directory:path}")
async def list_files(directory: str = ""):
    """列出目錄中的文件"""
    try:
        return file_service.list_files(directory)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"列出文件失敗: {str(e)}")

@app.get("/api/files")
async def get_files():
    """獲取可用檔案清單"""
    try:
        return file_service.get_files()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取檔案清單失敗: {str(e)}")

@app.post("/api/analysis/start", response_model=AnalysisResponse)
async def start_analysis(request: AnalysisRequest):
    """開始分析任務"""
    try:
        result = analysis_service.start_analysis(request.user_input, request.options)
        return AnalysisResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"開始分析失敗: {str(e)}")

@app.get("/api/analysis/{analysis_id}/status")
async def get_analysis_status(analysis_id: str):
    """獲取分析狀態"""
    return analysis_service.get_analysis_status(analysis_id)

@app.get("/api/agents/status")
async def get_agents_status():
    """獲取代理狀態"""
    try:
        return system_service.get_agents_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取代理狀態失敗: {str(e)}")

@app.post("/api/settings")
async def update_settings(request: SettingsRequest):
    """更新設定"""
    try:
        # TODO: 實現設定持久化邏輯
        # 目前僅返回成功消息
        return {"status": "settings updated", "timestamp": datetime.now().isoformat()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新設定失敗: {str(e)}")

@app.get("/health")
async def health_check():
    """健康檢查端點"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/")
async def root():
    """根端點"""
    return {
        "message": "多代理數據分析系統 API",
        "version": "1.0.0",
        "docs": "/docs"
    }



# 啟動服務器
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=5001,
        reload=True,
        log_level="info"
    )