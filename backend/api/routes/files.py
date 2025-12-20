"""文件相關的 API 路由。"""

from typing import Optional

from fastapi import APIRouter, HTTPException, UploadFile, File, Query
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

# 導入服務層
from core.services.file_service import FileService

# 導入模型
from api.models.files import FileContentResponse

# 建立路由器
router = APIRouter()

# 初始化服務
file_service = FileService()


class RenameRequest(BaseModel):
    """Request model for file rename."""
    newName: str


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


@router.post("/api/files/upload")
async def upload_file(
    file: UploadFile = File(...),
    directory: str = Query("", description="Target directory for upload")
):
    """Upload a file."""
    try:
        content = await file.read()
        result = file_service.save_uploaded_file(
            filename=file.filename or "unnamed_file",
            content=content,
            directory=directory
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/api/files/download/{filename:path}")
async def download_file(filename: str):
    """Download a file."""
    try:
        file_path = file_service.get_file_for_download(filename)
        return FileResponse(
            path=file_path,
            filename=file_path.name,
            media_type="application/octet-stream"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")


@router.delete("/api/files/{filename:path}")
async def delete_file(filename: str):
    """Delete a file."""
    try:
        return file_service.delete_file(filename)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")


@router.post("/api/files/{filename:path}/rename")
async def rename_file(filename: str, request: RenameRequest):
    """Rename a file."""
    try:
        return file_service.rename_file(filename, request.newName)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rename failed: {str(e)}")


@router.get("/api/files/preview/{filename:path}")
async def preview_file(filename: str):
    """Preview a file (images, PDFs, text files)."""
    try:
        preview_info = file_service.get_file_preview(filename)
        return FileResponse(
            path=preview_info["path"],
            filename=preview_info["filename"],
            media_type=preview_info["mime_type"]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Preview failed: {str(e)}")


@router.get("/api/files/search")
async def search_files(
    query: str = Query("", description="Search query for filename"),
    fileType: str = Query("", description="Filter by file extension"),
    dateStart: str = Query("", description="Min modification date (ISO format)"),
    dateEnd: str = Query("", description="Max modification date (ISO format)"),
    sizeMin: int = Query(0, description="Min file size in bytes"),
    sizeMax: int = Query(0, description="Max file size in bytes")
):
    """Search files with filters."""
    try:
        results = file_service.search_files(
            query=query,
            file_type=fileType,
            date_start=dateStart,
            date_end=dateEnd,
            size_min=sizeMin,
            size_max=sizeMax
        )
        return {"files": results, "total_count": len(results)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")