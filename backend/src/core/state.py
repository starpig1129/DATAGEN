from typing import Sequence, TypedDict, Annotated
from typing_extensions import NotRequired


from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class State(TypedDict):
    """TypedDict for the entire state structure."""
    # The sequence of messages exchanged in the conversation
    messages: Annotated[Sequence[BaseMessage], add_messages]

    # The complete content of the research hypothesis
    hypothesis: NotRequired[str]
    
    # The complete content of the research process
    process: NotRequired[str]
    
    # next process
    process_decision: NotRequired[str]
    
    # The current state of data visualization planning and execution
    visualization_state: NotRequired[str]
    
    # The current state of the search process, including queries and results
    searcher_state: NotRequired[str]
    
    # The current state of Coder development, including scripts and outputs
    code_state: NotRequired[str]
    
    # The content of the report sections being written
    report_section: NotRequired[str]
    
    # The feedback and comments from the quality review process
    quality_review: NotRequired[str]
    
    # A boolean flag indicating if the current output requires revision
    needs_revision: NotRequired[bool]
    
    # The identifier of the agent who sent the last message
    sender: NotRequired[str]


