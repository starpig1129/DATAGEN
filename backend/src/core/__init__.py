import sys
from pathlib import Path

# 調整路徑以支援模組導入
backend_path = str(Path(__file__).resolve().parent.parent.parent)
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

try:
    from .workflow import WorkflowManager
    from .language_models import LanguageModelManager
    from .node import agent_node, human_choice_node, note_agent_node, human_review_node, refiner_node
    from .router import QualityReview_router, hypothesis_router, process_router
except ImportError:
    # 如果相對導入失敗，嘗試絕對導入
    from src.core.workflow import WorkflowManager
    from src.core.language_models import LanguageModelManager
    from src.core.node import agent_node, human_choice_node, note_agent_node, human_review_node, refiner_node
    from src.core.router import QualityReview_router, hypothesis_router, process_router