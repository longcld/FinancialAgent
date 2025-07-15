from langgraph.graph import END, StateGraph, START, MessagesState
from langgraph.managed import IsLastStep, RemainingSteps
from langchain_core.messages import AnyMessage

from typing import List


class State(MessagesState):
    """Base state for the graph."""
    history: List[AnyMessage]
    next: str
    plan: str
    is_last_step: IsLastStep
    remaining_steps: RemainingSteps
    
