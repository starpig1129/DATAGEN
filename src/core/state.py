from typing import Sequence, List, Optional
from pydantic import BaseModel, Field

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class State(BaseModel):
    """
    Canonical shared state for the multi-agent research workflow.

    Design goals:
    - Strong type safety via Pydantic
    - JSON serializable (checkpoint / resume friendly)
    - Backward compatible (all fields optional or defaulted)
    - LangGraph reducer support for messages
    """

    # ======================================================
    # Conversation Layer (LangGraph-managed)
    # ======================================================
    messages: Sequence[BaseMessage] = Field(
        default_factory=list,
        description="Sequence of messages exchanged in the workflow",
        json_schema_extra={"reducer": add_messages},
    )

    sender: Optional[str] = Field(
        default=None,
        description="Identifier of the agent who last updated the state",
    )

    # ======================================================
    # Core Research Artifacts (Source of Truth)
    # ======================================================
    hypothesis: Optional[str] = None

    literature_summary: Optional[str] = None

    datasets_used: List[str] = Field(default_factory=list)

    code_artifacts: List[str] = Field(
        default_factory=list,
        description="Paths or identifiers of generated code artifacts",
    )

    visualizations: List[str] = Field(
        default_factory=list,
        description="Paths or identifiers of generated visualization files",
    )

    report_draft: Optional[str] = None

    references: List[str] = Field(default_factory=list)

    # ======================================================
    # Review & Refinement
    # ======================================================
    quality_feedback: Optional[str] = None

    needs_revision: bool = Field(
        default=False,
        description="Indicates whether the current output requires revision",
    )

    # ======================================================
    # Supervisor / Routing Metadata
    # ======================================================
    process_decision: Optional[str] = Field(
        default=None,
        description="Next agent or step selected by the supervisor",
    )

    process_reason: Optional[str] = Field(
        default=None,
        description="Reason for the supervisor's routing decision",
    )

    # ======================================================
    # Legacy / Transitional Fields (Backward Compatible)
    # ======================================================
    process: Optional[str] = None

    searcher_state: Optional[str] = None

    code_state: Optional[str] = None

    visualization_state: Optional[str] = None

    report_section: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True
        validate_assignment = True
