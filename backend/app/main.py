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

# 導入 API 路由
from api.routes import root_router, system_router, files_router, analysis_router, settings_router

# 包含路由到主應用程式
app.include_router(root_router, tags=["root"])
app.include_router(system_router, prefix="/api/system", tags=["system"])
app.include_router(files_router, prefix="/api/files", tags=["files"])
app.include_router(analysis_router, prefix="/api/analysis", tags=["analysis"])
app.include_router(settings_router, prefix="/api/settings", tags=["settings"])



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