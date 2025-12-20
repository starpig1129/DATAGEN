"""應用程式主入口。"""

import os

# 導入系統組件
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI

from app.factory import create_app

# 建立應用程式實例
app = create_app()


def setup_routes():
    """設置路由，避免循環導入"""
    # 導入 API 路由
    from api.routes import (
        root_router, system_router, files_router,
        analysis_router, settings_router, auth_router
    )

    # 包含路由到主應用程式
    app.include_router(root_router, tags=["root"])
    app.include_router(system_router, tags=["system"])
    app.include_router(files_router, tags=["files"])
    app.include_router(analysis_router, tags=["analysis"])
    app.include_router(settings_router, tags=["settings"])
    app.include_router(auth_router, tags=["auth"])


# 設置路由
setup_routes()



# 啟動服務器
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=5001,
        reload=True,
        log_level="info"
    )