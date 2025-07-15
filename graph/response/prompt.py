from langchain_core.prompts import ChatPromptTemplate

RESPONSE_PROMPT = """You are a helpful assistant. You will receive the results of the workers and you need to respond to the user with the final result.

# Response style
- Use markdown to format your response.
- Always response in Vietnamese.
- Do not skip any information resulted from the workers."""

response_prompt = ChatPromptTemplate.from_messages([
    ("system", RESPONSE_PROMPT),
    ("placeholder", "{history}"),
    ("placeholder", "{messages}")
])