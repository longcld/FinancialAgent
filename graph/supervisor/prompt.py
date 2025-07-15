import json
from langchain_core.prompts import ChatPromptTemplate

from graph.file_controler.tools import tools as file_control_tools
from graph.analyzer.tools import tools as analyzer_tools

from logger import logger

agent_members = {
    "file_controler": {
        "description": "Responsible for preprocessing the raw file and writing it to the system. Can only write, not read or analyze.",
        "tools": [{tool.name: tool.description} for tool in file_control_tools]
    },
    "analyzer": {
        "description": "Financial Analyst expert who has full access to all the uploaded files in the system and analyze its content",
        "tools": [{tool.name: tool.description} for tool in analyzer_tools]
    }
}

members = ""
for agent, details in agent_members.items():
    members += f"- {agent}: {details['description']}\n"

tools_description = ""
for agent, details in agent_members.items():
    tools_description += f"\n{agent} tools:\n"
    for tool in details["tools"]:
        for name, desc in tool.items():
            tools_description += f"  - {name}: {desc}\n"

logger.debug(f"Members description:\n{members}")
logger.debug(f"Tools description:\n{tools_description}")

SUPERVISOR_PROMPT = f"""You are a supervisor tasked with managing a conversation between the following workers:
{members}
Given the following user request, respond with the worker to act next. Each worker will perform a task and respond with their results and status.
When finished, respond with FINISH."""

supervisor_prompt = ChatPromptTemplate.from_messages([
    ("system", SUPERVISOR_PROMPT),
    ("human", "{plan}"),
    ("placeholder", "{history}"),
    ("placeholder", "{messages}")
])