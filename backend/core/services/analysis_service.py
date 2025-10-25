"""分析服務層模組。"""

import asyncio
from datetime import datetime
from typing import Dict, Any, Optional

from fastapi import HTTPException

# 導入系統組件
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.system import MultiAgentSystem


class AnalysisService:
    """分析任務相關業務邏輯服務。"""

    def __init__(self, ws_manager=None):
        """初始化分析服務。

        Args:
            ws_manager: WebSocket 管理器實例，用於發送狀態更新。
        """
        self.ws_manager = ws_manager

    def start_analysis(self, user_input: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """開始分析任務。

        Args:
            user_input: 用戶輸入。
            options: 分析選項。

        Returns:
            包含分析 ID、狀態和消息的字典。

        Raises:
            HTTPException: 如果開始失敗。
        """
        try:
            analysis_id = f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # 在後台啟動分析任務
            asyncio.create_task(self.run_analysis_async(analysis_id, user_input, options))

            return {
                "analysis_id": analysis_id,
                "status": "started",
                "message": "分析任務已開始",
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"開始分析失敗: {str(e)}")

    def get_analysis_status(self, analysis_id: str) -> Dict[str, Any]:
        """獲取分析狀態。

        Args:
            analysis_id: 分析 ID。

        Returns:
            包含分析狀態的字典。
        """
        # TODO: 實現分析狀態追蹤
        return {
            "analysis_id": analysis_id,
            "status": "running",
            "progress": 0,
            "message": "分析進行中",
            "timestamp": datetime.now().isoformat()
        }

    async def run_analysis_async(self, analysis_id: str, user_input: str, options: Optional[Dict[str, Any]] = None):
        """異步運行分析任務。

        Args:
            analysis_id: 分析 ID。
            user_input: 用戶輸入。
            options: 分析選項。
        """
        try:
            # 建立 MultiAgentSystem 實例
            system = MultiAgentSystem()

            # 定義 WebSocket 回調函數
            def websocket_callback(agent_id: str, status: str, progress: int, task: str):
                """WebSocket 回調函數，用於廣播代理狀態更新。"""
                if self.ws_manager:
                    try:
                        loop = asyncio.get_running_loop()
                        loop.create_task(self.ws_manager.send_agent_status(agent_id, status, progress, task))
                    except RuntimeError:
                        # 沒有運行的事件循環，創建新的
                        asyncio.run(self.ws_manager.send_agent_status(agent_id, status, progress, task))

            # 運行分析
            system.run(user_input, websocket_callback=websocket_callback)

            print(f"分析完成: {analysis_id}")

        except Exception as e:
            print(f"分析失敗 {analysis_id}: {e}")
            # 發送錯誤消息到 WebSocket
            if self.ws_manager:
                try:
                    loop = asyncio.get_running_loop()
                    loop.create_task(self.ws_manager.send_agent_status(
                        "system",
                        "error",
                        0,
                        f"分析失敗: {str(e)}"
                    ))
                except RuntimeError:
                    asyncio.run(self.ws_manager.send_agent_status(
                        "system",
                        "error",
                        0,
                        f"分析失敗: {str(e)}"
                    ))