from langchain_openai import ChatOpenAI
from langgraph.types import Command
from langchain_core.messages import HumanMessage

from graph.state import State
from graph.response.prompt import response_prompt

from config import configs
from logger import logger

response_agent = response_prompt | ChatOpenAI(model=configs.llm_model_name, temperature=0)
