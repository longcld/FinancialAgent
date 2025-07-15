from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from graph.state import State
from langgraph.types import Command

from typing import Literal

from graph.state import State
from graph.analyzer.prompt import analyzer_prompt
from graph.analyzer.tools import tools
from config import configs


model = ChatOpenAI(
    model=configs.llm_model_name,
    api_key=configs.openai_api_key,
    temperature=0.0,
    streaming=True
)

analyzer_agent = create_react_agent(
    model,
    tools,
    prompt=analyzer_prompt,
    name="analyzer",
    state_schema=State,
)

def analyzer_graph(state: State) -> Command[Literal["supervisor"]]:
    result = analyzer_agent.invoke(state)
    return Command(
        update={
            "messages": [
                HumanMessage(content=result["messages"][-1].content, name="analyzer")
            ]
        },
        goto="supervisor",
    )