import re
from logger import logger

from langgraph.graph import END, StateGraph, START
from langgraph.types import Command

from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage, AIMessage

from graph.state import State


from memory.local import local_memory_manager
from utils import get_user_id

def load_memory(state: State, config: RunnableConfig):
    """
    Loads the memory from the database.
    This function retrieves the messages from the state and returns the state.
    """
    # Load memory process
    logger.debug(f"User ID: {get_user_id(config)}")

    history = local_memory_manager.load_messages(config)

    return Command(
        update={
            "history": history,
        }
    )

def update_memory(state: State, config: RunnableConfig):
    """
    Updates the memory with the latest message.
    This function retrieves the latest message from the state and updates the memory.
    """
    # Update memory process
    message = state['messages'][-1]

    local_memory_manager.add_message(
        message=message,
        config=config
    )

memory_agent = StateGraph(State)

memory_agent.add_node("add_message", update_memory)
memory_agent.add_node("load_memory", load_memory)

memory_agent.add_edge(START, "add_message")
memory_agent.add_edge("add_message", "load_memory")
memory_agent.add_edge("load_memory", END)

memory_graph = memory_agent.compile()