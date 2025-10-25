"""分析相關的 API 路由。"""

from fastapi import APIRouter, HTTPException

# 導入服務層
from core.services.analysis_service import AnalysisService

# 導入模型
from api.models.analysis import AnalysisRequest, AnalysisResponse

# 導入 WebSocket 相關
from websocket.manager import ws_manager

# 建立路由器
router = APIRouter()

# 初始化服務
analysis_service = AnalysisService(ws_manager)


@router.post("/api/analysis/start", response_model=AnalysisResponse)
async def start_analysis(request: AnalysisRequest):
    """開始分析任務"""
    try:
        result = analysis_service.start_analysis(request.user_input, request.options)
        return AnalysisResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"開始分析失敗: {str(e)}")


@router.get("/api/analysis/{analysis_id}/status")
async def get_analysis_status(analysis_id: str):
    """獲取分析狀態"""
    return analysis_service.get_analysis_status(analysis_id)