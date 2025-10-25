"""CORS 設定管理。"""

from fastapi.middleware.cors import CORSMiddleware


def get_cors_settings():
    """取得 CORS 設定參數。

    Returns:
        dict: CORS 設定參數字典。
    """
    return {
        "allow_origins": ["http://localhost:5173", "http://localhost:3000"],  # 前端開發服務器
        "allow_credentials": True,
        "allow_methods": ["*"],
        "allow_headers": ["*"],
    }