from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    user_id: str = Field(
        ...,
        title='User ID',
        description='Unique identifier for the user making the request',
        example='123456'
    )
    session_id: str = Field(
        ...,
        title='Session ID',
        description='Unique identifier for the session associated with the request',
        example='session_abc'
    )
    message: str = Field(
        ...,
        title="User's message content",
        description='The question or prompt the user is asking',
        example='hi xin chao'
    )
    params: dict = Field(
        default={},
        title='Parameters',
        description='Additional parameters for the chat request',
        example={}
    )