"""設定相關的資料模型。"""

from typing import Dict, Any
from pydantic import BaseModel


class SettingsRequest(BaseModel):
    """設定請求"""
    settings: Dict[str, Any]