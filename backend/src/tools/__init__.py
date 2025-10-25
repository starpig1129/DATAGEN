import sys
from pathlib import Path

# 調整路徑以支援模組導入
backend_path = str(Path(__file__).resolve().parent.parent.parent)
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

try:
    from .basetool import execute_code, execute_command
    from .FileEdit import create_document, read_document, edit_document, collect_data
    from .internet import google_search, scrape_webpages
except ImportError:
    # 如果相對導入失敗，嘗試絕對導入
    from src.tools.basetool import execute_code, execute_command
    from src.tools.FileEdit import create_document, read_document, edit_document, collect_data
    from src.tools.internet import google_search, scrape_webpages

__all__ = [
    "execute_code",
    "execute_command",
    "create_document",
    "read_document",
    "edit_document",
    "collect_data",
    "google_search",
    "scrape_webpages",
]