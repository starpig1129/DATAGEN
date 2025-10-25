"""檔案服務層模組。"""

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

from fastapi import HTTPException


class FileService:
    """檔案相關業務邏輯服務。"""

    def __init__(self):
        """初始化檔案服務。"""
        self.base_path = Path.cwd()

    def get_file_content(self, file_path: str) -> Dict[str, Any]:
        """獲取文件內容。

        Args:
            file_path: 相對文件路徑。

        Returns:
            包含文件內容、編碼、大小和修改時間的字典。

        Raises:
            HTTPException: 如果文件不存在、無效路徑或讀取失敗。
        """
        # 安全檢查：防止路徑遍歷攻擊
        if ".." in file_path or file_path.startswith("/"):
            raise HTTPException(status_code=400, detail="無效的文件路徑")

        # 構造完整路徑
        full_path = (self.base_path / file_path).resolve()

        # 確保文件在專案目錄內
        if not str(full_path).startswith(str(self.base_path)):
            raise HTTPException(status_code=403, detail="禁止訪問")

        # 檢查文件是否存在
        if not full_path.exists():
            raise HTTPException(status_code=404, detail="文件不存在")

        # 檢查是否為文件
        if not full_path.is_file():
            raise HTTPException(status_code=400, detail="路徑不是文件")

        # 讀取文件內容
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            encoding = 'utf-8'
        except UnicodeDecodeError:
            # 如果 UTF-8 失敗，嘗試其他編碼
            try:
                with open(full_path, 'r', encoding='latin-1') as f:
                    content = f.read()
                encoding = 'latin-1'
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"無法讀取文件內容: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"讀取文件失敗: {str(e)}")

        # 獲取文件信息
        stat = full_path.stat()

        return {
            "content": content,
            "encoding": encoding,
            "size": stat.st_size,
            "last_modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
        }

    def list_files(self, directory: str = "") -> Dict[str, Any]:
        """列出目錄中的文件。

        Args:
            directory: 相對目錄路徑，預設為根目錄。

        Returns:
            包含目錄路徑、文件列表和總數的字典。

        Raises:
            HTTPException: 如果目錄不存在、無效路徑或讀取失敗。
        """
        # 安全檢查
        if ".." in directory or (directory and directory.startswith("/")):
            raise HTTPException(status_code=400, detail="無效的目錄路徑")

        # 構造完整路徑
        if directory:
            full_path = (self.base_path / directory).resolve()
        else:
            full_path = self.base_path

        # 確保目錄在專案目錄內
        if not str(full_path).startswith(str(self.base_path)):
            raise HTTPException(status_code=403, detail="禁止訪問")

        # 檢查是否為目錄
        if not full_path.exists():
            raise HTTPException(status_code=404, detail="目錄不存在")

        if not full_path.is_dir():
            raise HTTPException(status_code=400, detail="路徑不是目錄")

        # 獲取文件列表
        files = []
        for item in full_path.iterdir():
            if item.is_file():
                stat = item.stat()
                files.append({
                    "name": item.name,
                    "path": str(item.relative_to(self.base_path)),
                    "size": stat.st_size,
                    "last_modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "is_file": True
                })
            elif item.is_dir():
                files.append({
                    "name": item.name,
                    "path": str(item.relative_to(self.base_path)),
                    "is_file": False
                })

        return {
            "directory": str(full_path.relative_to(self.base_path)) if full_path != self.base_path else "",
            "files": files,
            "total_count": len(files)
        }

    def get_files(self) -> Dict[str, Any]:
        """獲取可用檔案清單（根目錄）。

        Returns:
            包含目錄路徑、文件列表和總數的字典。

        Raises:
            HTTPException: 如果讀取失敗。
        """
        return self.list_files("")  # 直接呼叫 list_files 處理根目錄