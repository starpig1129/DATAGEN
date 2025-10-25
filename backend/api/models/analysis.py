"""分析相關的資料模型。"""

from typing import Dict, Any, Optional
from pydantic import BaseModel


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