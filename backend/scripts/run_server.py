#!/usr/bin/env python3
"""
FastAPI 伺服器啟動腳本
統一的應用程式啟動方式
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=5001,
        reload=True,
        log_level="info"
    )