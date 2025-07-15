from langchain_core.prompts import ChatPromptTemplate

FILE_CONTROL_PROMPT = """# <Role>
- You are a file control agent that can preprocess files uploaded by users. Your main task is to extract the content of the uploaded files and store them in the system for future use.
- You could not analyze the content of the file.
- Don't ask follow-up questions."""

file_control_prompt = ChatPromptTemplate.from_messages([
    ("system", FILE_CONTROL_PROMPT),
    ("placeholder", "{history}"),
    ("placeholder", "{messages}")
])