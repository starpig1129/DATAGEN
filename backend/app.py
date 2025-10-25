"""
FastAPI 後端服務器
提供 HTTP API 服務給前端應用程式
"""

import os
import json
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# 導入系統組件
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.system import MultiAgentSystem
from websocket_server import ws_manager

# 創建 FastAPI 應用程式
app = FastAPI(
    title="多代理數據分析系統 API",
    description="提供後端 API 服務",
    version="1.0.0"
)

# 添加 CORS 中間件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # 前端開發服務器
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# API 路由

@app.get("/api/system/status", response_model=SystemStatusResponse)
async def get_system_status():
    """獲取系統狀態"""
    try:
        return SystemStatusResponse(
            status="healthy",
            timestamp=datetime.now().isoformat(),
            version="1.0.0",
            websocket_connections=len(ws_manager.connections),
            system_info={
                "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                "working_directory": os.getcwd(),
                "available_agents": [
                    "hypothesis_agent",
                    "process_agent",
                    "search_agent",
                    "code_agent",
                    "visualization_agent",
                    "report_agent",
                    "quality_review_agent",
                    "note_agent",
                    "refiner_agent"
                ]
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取系統狀態失敗: {str(e)}")

@app.get("/api/files/content/{file_path:path}", response_model=FileContentResponse)
async def get_file_content(file_path: str):
    """獲取文件內容"""
    try:
        # 安全檢查：防止路徑遍歷攻擊
        if ".." in file_path or file_path.startswith("/"):
            raise HTTPException(status_code=400, detail="無效的文件路徑")

        # 構造完整路徑
        base_path = Path.cwd()
        full_path = (base_path / file_path).resolve()

        # 確保文件在專案目錄內
        if not str(full_path).startswith(str(base_path)):
            raise HTTPException(status_code=403, detail="禁止訪問")

        # 檢查文件是否存在
        if not full_path.exists():
            raise HTTPException(status_code=404, detail="文件不存在")

        # 檢查是否為文件
        if not full_path.is_file():
            raise HTTPException(status_code=400, detail="路徑不是文件")

        # 讀取文件內容
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            # 如果 UTF-8 失敗，嘗試其他編碼
            try:
                with open(full_path, 'r', encoding='latin-1') as f:
                    content = f.read()
                encoding = 'latin-1'
            except Exception:
                raise HTTPException(status_code=500, detail="無法讀取文件內容")
        else:
            encoding = 'utf-8'

        # 獲取文件信息
        stat = full_path.stat()

        return FileContentResponse(
            content=content,
            encoding=encoding,
            size=stat.st_size,
            last_modified=datetime.fromtimestamp(stat.st_mtime).isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"讀取文件失敗: {str(e)}")

@app.get("/api/files/list/{directory:path}")
async def list_files(directory: str = ""):
    """列出目錄中的文件"""
    try:
        # 安全檢查
        if ".." in directory or (directory and directory.startswith("/")):
            raise HTTPException(status_code=400, detail="無效的目錄路徑")

        # 構造完整路徑
        base_path = Path.cwd()
        if directory:
            full_path = (base_path / directory).resolve()
        else:
            full_path = base_path

        # 確保目錄在專案目錄內
        if not str(full_path).startswith(str(base_path)):
            raise HTTPException(status_code=403, detail="禁止訪問")

        # 檢查是否為目錄
        if not full_path.exists():
            raise HTTPException(status_code=404, detail="目錄不存在")

        if not full_path.is_dir():
            raise HTTPException(status_code=400, detail="路徑不是目錄")

        # 獲取文件列表
        files = []
        for item in full_path.iterdir():
            if item.is_file():
                stat = item.stat()
                files.append({
                    "name": item.name,
                    "path": str(item.relative_to(base_path)),
                    "size": stat.st_size,
                    "last_modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "is_file": True
                })
            elif item.is_dir():
                files.append({
                    "name": item.name,
                    "path": str(item.relative_to(base_path)),
                    "is_file": False
                })

        return {
            "directory": str(full_path.relative_to(base_path)) if full_path != base_path else "",
            "files": files,
            "total_count": len(files)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"列出文件失敗: {str(e)}")

@app.post("/api/analysis/start", response_model=AnalysisResponse)
async def start_analysis(request: AnalysisRequest):
    """開始分析任務"""
    try:
        analysis_id = f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # 在後台啟動分析任務
        asyncio.create_task(run_analysis_async(analysis_id, request.user_input, request.options))

        return AnalysisResponse(
            analysis_id=analysis_id,
            status="started",
            message="分析任務已開始",
            timestamp=datetime.now().isoformat()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"開始分析失敗: {str(e)}")

@app.get("/api/analysis/{analysis_id}/status")
async def get_analysis_status(analysis_id: str):
    """獲取分析狀態"""
    # TODO: 實現分析狀態追蹤
    return {
        "analysis_id": analysis_id,
        "status": "running",
        "progress": 0,
        "message": "分析進行中",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/agents/status")
async def get_agents_status():
    """獲取代理狀態"""
    try:
        # 從 WebSocket 管理器獲取連接信息
        return {
            "websocket_connections": len(ws_manager.connections),
            "active_agents": [
                "hypothesis_agent",
                "process_agent",
                "search_agent",
                "code_agent",
                "visualization_agent",
                "report_agent",
                "quality_review_agent",
                "note_agent",
                "refiner_agent"
            ],
            "system_status": "healthy",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取代理狀態失敗: {str(e)}")

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

# 異步分析任務
async def run_analysis_async(analysis_id: str, user_input: str, options: Optional[Dict[str, Any]] = None):
    """異步運行分析任務"""
    try:
        # 建立 MultiAgentSystem 實例
        system = MultiAgentSystem()

        # 定義 WebSocket 回調函數
        def websocket_callback(agent_id: str, status: str, progress: int, task: str):
            """WebSocket 回調函數，用於廣播代理狀態更新"""
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(ws_manager.send_agent_status(agent_id, status, progress, task))
            except RuntimeError:
                # 沒有運行的事件循環，創建新的
                asyncio.run(ws_manager.send_agent_status(agent_id, status, progress, task))

        # 運行分析
        system.run(user_input, websocket_callback=websocket_callback)

        print(f"分析完成: {analysis_id}")

    except Exception as e:
        print(f"分析失敗 {analysis_id}: {e}")
        # 發送錯誤消息到 WebSocket
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(ws_manager.send_agent_status(
                "system",
                "error",
                0,
                f"分析失敗: {str(e)}"
            ))
        except RuntimeError:
            asyncio.run(ws_manager.send_agent_status(
                "system",
                "error",
                0,
                f"分析失敗: {str(e)}"
            ))

# 啟動服務器
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=5001,
        reload=True,
        log_level="info"
    )