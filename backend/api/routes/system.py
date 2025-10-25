"""系統相關的 API 路由。"""

from fastapi import APIRouter, HTTPException

# 導入服務層
from core.services.system_service import SystemService

# 導入模型
from api.models.system import SystemStatusResponse

# 導入 WebSocket 相關
from websocket_server.manager import ws_manager

# 建立路由器
router = APIRouter()

# 初始化服務
system_service = SystemService(ws_manager)


@router.get("/api/system/status", response_model=SystemStatusResponse)
async def get_system_status():
    """獲取系統狀態"""
    try:
        system_status = system_service.get_system_status()
        return SystemStatusResponse(**system_status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取系統狀態失敗: {str(e)}")


@router.get("/api/state")
async def get_state():
    """獲取應用程式狀態"""
    return system_service.get_state()


@router.get("/api/agents/status")
async def get_agents_status():
    """獲取代理狀態"""
    try:
        return system_service.get_agents_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取代理狀態失敗: {str(e)}")

