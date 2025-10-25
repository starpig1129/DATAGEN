"""文件相關的資料模型。"""

from pydantic import BaseModel


class FileContentResponse(BaseModel):
    """文件內容響應"""
    content: str
    encoding: str
    size: int
    last_modified: str