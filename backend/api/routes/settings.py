"""設定相關的 API 路由。"""

from datetime import datetime
from fastapi import APIRouter, HTTPException

# 導入模型
from api.models.settings import SettingsRequest

# 建立路由器
router = APIRouter()


@router.post("/api/settings")
async def update_settings(request: SettingsRequest):
    """更新設定"""
    try:
        # TODO: 實現設定持久化邏輯
        # 目前僅返回成功消息
        return {"status": "settings updated", "timestamp": datetime.now().isoformat()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新設定失敗: {str(e)}")