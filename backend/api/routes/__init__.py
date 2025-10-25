"""API 路由模組。"""

from .root import router as root_router
from .system import router as system_router
from .files import router as files_router
from .analysis import router as analysis_router
from .settings import router as settings_router

__all__ = [
    "root_router",
    "system_router",
    "files_router",
    "analysis_router",
    "settings_router",
]