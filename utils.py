import json
from langchain_core.runnables import RunnableConfig

from model.message import Message

def convert_to_sse_format(payload):
    return f"data: {json.dumps(payload)}\n\n"

def get_message_id(config: RunnableConfig) -> str:
    message_id = config["configurable"].get("message_id")
    if message_id is None:
        raise ValueError("Message ID needs to be provided to save a memory.")

    return message_id

def get_user_id(config: RunnableConfig) -> str:
    user_id = config["configurable"].get("user_id")
    if user_id is None:
        raise ValueError("User ID needs to be provided to save a memory.")

    return user_id

def get_session_id(config: RunnableConfig) -> str:
    session_id = config["configurable"].get("session_id")
    if session_id is None:
        raise ValueError("Session ID needs to be provided to save a memory.")

    return session_id

def convert_to_message(config: RunnableConfig) -> dict:
    """
    Convert the RunnableConfig to a Message object.
    """
    message_id = get_message_id(config)
    user_id = get_user_id(config)
    session_id = get_session_id(config)

    return Message(
        message_id=message_id,
        user_id=user_id,
        session_id=session_id,
        content=config["configurable"].get("content", "")
    )