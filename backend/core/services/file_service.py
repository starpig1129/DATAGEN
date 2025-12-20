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

    def save_uploaded_file(
        self, filename: str, content: bytes, directory: str = ""
    ) -> Dict[str, Any]:
        """Save an uploaded file.

        Args:
            filename: Name of the file to save.
            content: File content in bytes.
            directory: Target directory (relative path).

        Returns:
            Dict containing file info after upload.

        Raises:
            HTTPException: If save fails or path is invalid.
        """
        # Security check
        if ".." in filename or filename.startswith("/"):
            raise HTTPException(status_code=400, detail="Invalid filename")

        if directory and (".." in directory or directory.startswith("/")):
            raise HTTPException(status_code=400, detail="Invalid directory path")

        # Construct target path
        if directory:
            target_dir = (self.base_path / directory).resolve()
        else:
            target_dir = self.base_path / "data"

        # Ensure directory exists
        target_dir.mkdir(parents=True, exist_ok=True)

        # Ensure path is within project
        if not str(target_dir).startswith(str(self.base_path)):
            raise HTTPException(status_code=403, detail="Access denied")

        target_path = target_dir / filename

        try:
            with open(target_path, 'wb') as f:
                f.write(content)

            stat = target_path.stat()
            return {
                "name": filename,
                "path": str(target_path.relative_to(self.base_path)),
                "size": stat.st_size,
                "last_modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "message": "File uploaded successfully"
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    def get_file_for_download(self, filename: str) -> Path:
        """Get file path for download.

        Args:
            filename: Name or path of file to download.

        Returns:
            Path object to the file.

        Raises:
            HTTPException: If file doesn't exist or path is invalid.
        """
        # Security check
        if ".." in filename:
            raise HTTPException(status_code=400, detail="Invalid file path")

        # Try multiple locations
        possible_paths = [
            self.base_path / filename,
            self.base_path / "data" / filename,
        ]

        for full_path in possible_paths:
            full_path = full_path.resolve()
            if (str(full_path).startswith(str(self.base_path)) and
                    full_path.exists() and full_path.is_file()):
                return full_path

        raise HTTPException(status_code=404, detail="File not found")

    def delete_file(self, filename: str) -> Dict[str, Any]:
        """Delete a file.

        Args:
            filename: Name or path of file to delete.

        Returns:
            Dict with deletion status.

        Raises:
            HTTPException: If file doesn't exist or deletion fails.
        """
        # Security check
        if ".." in filename:
            raise HTTPException(status_code=400, detail="Invalid file path")

        # Try multiple locations
        possible_paths = [
            self.base_path / filename,
            self.base_path / "data" / filename,
        ]

        for full_path in possible_paths:
            full_path = full_path.resolve()
            if (str(full_path).startswith(str(self.base_path)) and
                    full_path.exists() and full_path.is_file()):
                try:
                    os.remove(full_path)
                    return {
                        "name": filename,
                        "deleted": True,
                        "message": "File deleted successfully"
                    }
                except Exception as e:
                    raise HTTPException(
                        status_code=500, detail=f"Failed to delete file: {str(e)}"
                    )

        raise HTTPException(status_code=404, detail="File not found")

    def rename_file(self, filename: str, new_name: str) -> Dict[str, Any]:
        """Rename a file.

        Args:
            filename: Current name or path of file.
            new_name: New filename.

        Returns:
            Dict with new file info.

        Raises:
            HTTPException: If file doesn't exist or rename fails.
        """
        # Security check
        if ".." in filename or ".." in new_name:
            raise HTTPException(status_code=400, detail="Invalid file path")

        if "/" in new_name or "\\" in new_name:
            raise HTTPException(status_code=400, detail="New name cannot contain path")

        # Try multiple locations
        possible_paths = [
            self.base_path / filename,
            self.base_path / "data" / filename,
        ]

        for full_path in possible_paths:
            full_path = full_path.resolve()
            if (str(full_path).startswith(str(self.base_path)) and
                    full_path.exists() and full_path.is_file()):
                new_path = full_path.parent / new_name

                # Check if new name already exists
                if new_path.exists():
                    raise HTTPException(
                        status_code=409, detail="A file with that name already exists"
                    )

                try:
                    os.rename(full_path, new_path)
                    stat = new_path.stat()
                    return {
                        "old_name": filename,
                        "new_name": new_name,
                        "path": str(new_path.relative_to(self.base_path)),
                        "size": stat.st_size,
                        "last_modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "message": "File renamed successfully"
                    }
                except Exception as e:
                    raise HTTPException(
                        status_code=500, detail=f"Failed to rename file: {str(e)}"
                    )

        raise HTTPException(status_code=404, detail="File not found")

    def get_file_preview(self, filename: str) -> Dict[str, Any]:
        """Get file info for preview.

        Args:
            filename: Name or path of file.

        Returns:
            Dict with file path and mime type for preview.

        Raises:
            HTTPException: If file doesn't exist.
        """
        full_path = self.get_file_for_download(filename)

        # Determine MIME type
        extension = full_path.suffix.lower()
        mime_types = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
            '.svg': 'image/svg+xml',
            '.pdf': 'application/pdf',
            '.txt': 'text/plain',
            '.md': 'text/markdown',
            '.csv': 'text/csv',
            '.json': 'application/json',
            '.html': 'text/html',
        }

        return {
            "path": full_path,
            "mime_type": mime_types.get(extension, 'application/octet-stream'),
            "filename": full_path.name
        }

    def search_files(
        self,
        query: str = "",
        file_type: str = "",
        date_start: str = "",
        date_end: str = "",
        size_min: int = 0,
        size_max: int = 0
    ) -> List[Dict[str, Any]]:
        """Search files with various filters.

        Args:
            query: Search query for filename.
            file_type: Filter by file extension.
            date_start: Filter by min modification date (ISO format).
            date_end: Filter by max modification date (ISO format).
            size_min: Filter by min size in bytes.
            size_max: Filter by max size in bytes.

        Returns:
            List of matching files.
        """
        results = []
        search_dir = self.base_path / "data"

        if not search_dir.exists():
            search_dir = self.base_path

        def search_recursive(directory: Path):
            try:
                for item in directory.iterdir():
                    if item.is_file():
                        # Apply filters
                        if query and query.lower() not in item.name.lower():
                            continue

                        if file_type:
                            if not item.suffix.lower().lstrip('.') == file_type.lower():
                                continue

                        stat = item.stat()

                        if size_min and stat.st_size < size_min:
                            continue

                        if size_max and stat.st_size > size_max:
                            continue

                        mod_time = datetime.fromtimestamp(stat.st_mtime)

                        if date_start:
                            try:
                                start = datetime.fromisoformat(date_start)
                                if mod_time < start:
                                    continue
                            except ValueError:
                                pass

                        if date_end:
                            try:
                                end = datetime.fromisoformat(date_end)
                                if mod_time > end:
                                    continue
                            except ValueError:
                                pass

                        results.append({
                            "name": item.name,
                            "path": str(item.relative_to(self.base_path)),
                            "size": stat.st_size,
                            "last_modified": mod_time.isoformat(),
                            "is_file": True
                        })

                    elif item.is_dir() and not item.name.startswith('.'):
                        search_recursive(item)
            except PermissionError:
                pass

        search_recursive(search_dir)
        return results