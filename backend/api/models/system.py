"""系統相關的資料模型。"""

from typing import Dict, Any
from pydantic import BaseModel


class SystemStatusResponse(BaseModel):
    """系統狀態響應"""
    status: str
    timestamp: str
    version: str
    websocket_connections: int
    system_info: Dict[str, Any]