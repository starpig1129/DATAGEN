"""文件相關的 API 路由。"""

from fastapi import APIRouter, HTTPException

# 導入服務層
from core.services.file_service import FileService

# 導入模型
from api.models.files import FileContentResponse

# 建立路由器
router = APIRouter()

# 初始化服務
file_service = FileService()


@router.get("/api/files/content/{file_path:path}", response_model=FileContentResponse)
async def get_file_content(file_path: str):
    """獲取文件內容"""
    try:
        file_data = file_service.get_file_content(file_path)
        return FileContentResponse(**file_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"讀取文件失敗: {str(e)}")


@router.get("/api/files/list/{directory:path}")
async def list_files(directory: str = ""):
    """列出目錄中的文件"""
    try:
        return file_service.list_files(directory)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"列出文件失敗: {str(e)}")


@router.get("/api/files")
async def get_files():
    """獲取可用檔案清單"""
    try:
        return file_service.get_files()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取檔案清單失敗: {str(e)}")