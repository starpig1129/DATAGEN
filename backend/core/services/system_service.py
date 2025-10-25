"""系統服務層模組。"""

import sys
from datetime import datetime
from typing import Dict, Any, List

from fastapi import HTTPException


class SystemService:
    """系統相關業務邏輯服務。"""

    def __init__(self, ws_manager=None):
        """初始化系統服務。

        Args:
            ws_manager: WebSocket 管理器實例，用於獲取連接信息。
        """
        self.ws_manager = ws_manager

    def get_system_status(self) -> Dict[str, Any]:
        """獲取系統狀態。

        Returns:
            包含系統狀態信息的字典。

        Raises:
            HTTPException: 如果獲取失敗。
        """
        try:
            websocket_connections = len(self.ws_manager.connections) if self.ws_manager else 0

            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "version": "1.0.0",
                "websocket_connections": websocket_connections,
                "system_info": {
                    "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                    "working_directory": sys.path[0] if sys.path else "",
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
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"獲取系統狀態失敗: {str(e)}")

    def get_agents_status(self) -> Dict[str, Any]:
        """獲取代理狀態。

        Returns:
            包含代理狀態信息的字典。

        Raises:
            HTTPException: 如果獲取失敗。
        """
        try:
            websocket_connections = len(self.ws_manager.connections) if self.ws_manager else 0

            return {
                "websocket_connections": websocket_connections,
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

    def get_state(self) -> Dict[str, Any]:
        """獲取應用程式狀態。

        Returns:
            包含應用程式狀態的字典。
        """
        return {
            "status": "ready",
            "agent_models": [],
            "version": "1.0.0"
        }