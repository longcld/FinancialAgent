from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from langchain_core.messages import AIMessage

from graph import app as vpbank_agent
from model.chat_request import ChatRequest
from model.message import Message

import uuid
from utils import convert_to_sse_format
from logger import logger

# Create a router instance
chat_router = APIRouter()


# Define routes within the router
@chat_router.post("/ainvoke")
async def ainvoke(
    request: ChatRequest
):
    logger.debug(f"Received request: {request}")

    agent_config = {
        "configurable": {
            "user_id": request.user_id,
            "thread_id": request.session_id,
            "session_id": request.session_id,
        }
    }

    inputs = {
        "messages": [
            {
                "role": "user",
                "content": request.message
            }
        ]
    }

    async def wrapped_streaming_tokens():
        old_node = None
        async for subgraph, state in vpbank_agent.astream(
                inputs,
                stream_mode="messages",
                subgraphs=True,
                config=agent_config,
            ):

            msg, metadata = state
            node = metadata["langgraph_node"]

            if old_node != node:
                yield convert_to_sse_format(
                    {
                        "content": f"\n**{node}**: \n",
                        "type": "think",
                    }
                )
                old_node = node

            if node == "responser":
                if msg.content:
                    if isinstance(msg, AIMessage):
                        yield convert_to_sse_format(
                            {
                                "content": msg.content,
                                "type": "msg"
                            }
                        )
            # elif node == "tools":
            #     # Handle tool calls
            #     pass
            else:
                if node != "tools":
                    if msg.content:
                        yield convert_to_sse_format(
                            {
                                "content": msg.content,
                                "type": "think"
                            }
                        )

    return StreamingResponse(
        wrapped_streaming_tokens(),
        media_type="text/event-stream",
        headers={
            "X-Content-Type-Options": "nosniff",
            "X-Accel-Buffering": "no",
            "Cache-Control": "no-cache, no-transform",
            "Connection": "keep-alive"
        }
    )



