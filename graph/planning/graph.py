from langchain_openai import ChatOpenAI
from langgraph.types import Command
from langchain_core.messages import HumanMessage

from graph.state import State
from graph.planning.prompt import planning_system_prompt

from config import configs
from logger import logger

planning_agent = planning_system_prompt | ChatOpenAI(model=configs.llm_model_name, temperature=0)

def planning_graph(state: State):

    logger.debug(f"Conversation history: {state['history']}")
    logger.debug(f"Get planning for messages: {state['messages']}")

    last_message = HumanMessage(f"Last user's message: {state['messages'][-1].content}")

    plan = planning_agent.invoke({
        "history": state['history'],
        "messages": [last_message],
    })

    logger.debug(f"Planning Result: {plan.content}")

    return Command(
        update={
            "plan": plan.content
        }
    )
