"""系統服務層模組。"""

import sys
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict

from fastapi import HTTPException


@dataclass
class ApplicationState:
    """Application state matching frontend BackendState interface."""
    messages: List[Dict[str, Any]] = field(default_factory=list)
    needs_decision: bool = False
    sender: str = ""
    hypothesis: str = ""
    process: str = ""
    process_decision: str = ""
    visualization_state: str = ""
    searcher_state: str = ""
    code_state: str = ""
    report_section: str = ""
    quality_review: str = ""
    needs_revision: bool = False


# Global application state (singleton pattern)
_app_state = ApplicationState()


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
        """獲取應用程式狀態 (matches frontend BackendState interface).

        Returns:
            包含應用程式狀態的字典，包括 messages, needs_decision 等。
        """
        return asdict(_app_state)

    @staticmethod
    def update_state(
        sender: Optional[str] = None,
        message: Optional[Dict[str, Any]] = None,
        needs_decision: Optional[bool] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Update application state and return the new state.

        Args:
            sender: Current agent/sender name.
            message: New message to append (format: {content, type, sender}).
            needs_decision: Whether user decision is required.
            **kwargs: Additional state fields to update.

        Returns:
            The updated application state.
        """
        global _app_state

        if sender is not None:
            _app_state.sender = sender
        if message is not None:
            _app_state.messages.append(message)
        if needs_decision is not None:
            _app_state.needs_decision = needs_decision

        # Update any additional fields
        for key, value in kwargs.items():
            if hasattr(_app_state, key):
                setattr(_app_state, key, value)

        return asdict(_app_state)

    @staticmethod
    def clear_state() -> None:
        """Reset application state to initial values."""
        global _app_state
        _app_state = ApplicationState()

    @staticmethod
    def get_current_state() -> Dict[str, Any]:
        """Get current application state as dict."""
        return asdict(_app_state)