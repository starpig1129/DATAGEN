from typing import Annotated, List, Dict, Optional, Any
from pydantic import BaseModel, ConfigDict, Field
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph.message import add_messages


class State(BaseModel):
    """
    Canonical shared state for the multi-agent research workflow.
    Designed as an 'Action Log' and 'Artifact Digest'.
    """
    
    model_config = ConfigDict(
        arbitrary_types_allowed=True, 
        validate_assignment=True,
        extra='ignore'
    )

    # === Context Layer ===
    messages: Annotated[List[BaseMessage], add_messages] = Field(
        default_factory=list,
        description="Sequence of messages exchanged in the workflow"
    )
    last_active_agent: Optional[str] = Field(
        default=None, 
        description="The last agent that performed an action"
    )
    step_count: int = Field(
        default=0, 
        description="Safety counter to prevent infinite loops"
    )

    # === Workflow Control ===
    current_instruction: Optional[str] = Field(
        default=None, 
        description="Specific task assigned to the next agent"
    )
    next_workflow_step: Optional[str] = Field(
        default=None, 
        description="The next node/agent to route to"
    )
    
    # === Task Tracking ===
    todo_list: List[str] = Field(
        default_factory=list, 
        description="List of pending subtasks"
    )
    completed_tasks: List[str] = Field(
        default_factory=list, 
        description="List of completed subtasks"
    )

    # === Domain Artifacts (Dict[Path, Description]) ===
    hypothesis: Optional[str] = Field(
        default=None, 
        description="Current research hypothesis"
    )
    
    search_artifacts: Dict[str, str] = Field(
        default_factory=dict, 
        description="Map of {path: summary} for search results"
    )
    data_viz_artifacts: Dict[str, str] = Field(
        default_factory=dict, 
        description="Map of {path: summary} for visualizations"
    )
    code_artifacts: Dict[str, str] = Field(
        default_factory=dict, 
        description="Map of {path: summary} for code files"
    )
    report_artifacts: Dict[str, str] = Field(
        default_factory=dict, 
        description="Map of {section: path/content} for report sections"
    )

    # === Review Loop ===
    quality_feedback: Optional[str] = Field(
        default=None, 
        description="Feedback from quality review"
    )
    needs_revision: bool = Field(
        default=False, 
        description="Flag to trigger revision loop"
    )
    revision_count: int = Field(
        default=0,
        description="Counter for consecutive revision attempts"
    )
    
    # === Legacy Compatibility (Optional) ===
    # Using properties or aliases if needed, but we are doing a hard break as requested.


def create_initial_state(user_input: str) -> dict:
    """
    Factory function to create the initial state dictionary for LangGraph.
    """
    return {
        "messages": [HumanMessage(content=user_input)],
        "last_active_agent": "user",
        "step_count": 0,
        "todo_list": [],
        "completed_tasks": [],
        "search_artifacts": {},
        "data_viz_artifacts": {},
        "code_artifacts": {},
        "report_artifacts": {},
        "needs_revision": False,
        "revision_count": 0
    }
