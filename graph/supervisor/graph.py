from typing import List, Optional, Literal
from typing_extensions import TypedDict

from langchain_openai import ChatOpenAI
from langgraph.types import Command

from graph.state import State
from graph.supervisor.prompt import agent_members, supervisor_prompt
from config import configs
from logger import logger


model = ChatOpenAI(
    model=configs.llm_model_name,
    api_key=configs.openai_api_key,
    temperature=0.0,
    streaming=True
)

options = ["FINISH"] + list(agent_members.keys())
class Router(TypedDict):
    """Worker to route to next. If no workers needed, route to FINISH."""
    next: Literal[*options] # type: ignore

supervisor_agent = supervisor_prompt | model.with_structured_output(Router)

def supervisor_graph(state: State) -> Command[Literal[*agent_members, "responser"]]: # type: ignore
    """An LLM-based router."""
    response = supervisor_agent.invoke(state)
    goto = response["next"]
    if goto == "FINISH":
        goto = "responser"

    logger.debug(f"Supervisor routing to: {goto}")
    return Command(goto=goto, update={"next": goto})

