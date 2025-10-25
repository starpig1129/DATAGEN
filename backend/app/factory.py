"""應用程式工廠模組。"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def create_app() -> FastAPI:
    """建立並設定 FastAPI 應用程式實例。

    Returns:
        FastAPI: 設定好的 FastAPI 應用程式實例。
    """
    from config.settings import APP_TITLE, APP_DESCRIPTION, APP_VERSION
    from config.cors import get_cors_settings

    app = FastAPI(
        title=APP_TITLE,
        description=APP_DESCRIPTION,
        version=APP_VERSION,
    )

    # 添加 CORS 中間件
    cors_settings = get_cors_settings()
    app.add_middleware(CORSMiddleware, **cors_settings)

    return app