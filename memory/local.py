import json
from pathlib import Path
from typing import List, Optional, Union
from uuid import uuid4
from config import configs
from langchain_core.chat_history import (
    BaseChatMessageHistory,
)
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.runnables import RunnableConfig

from model.message import Message
from utils import get_user_id, get_session_id, get_message_id
from loguru import logger

class LocalMemory():
    """Chat message history that stores messages in a local file."""

    def __init__(
        self,
        memory_length: int = 5,
    ):
        """Initialize the local chat message history."""

        self.encoding = "utf-8"
        self.ensure_ascii = False

        self.memory_length = memory_length

    def _get_path(self, config: RunnableConfig) -> Path:
        """Get the file path for the local memory."""
        user_id = get_user_id(config)
        session_id = get_session_id(config)

        folder_path = Path(configs.message_log_directory) / user_id
        file_path = folder_path / f"{session_id}.json"

        return folder_path, file_path
    
    def _init_path(self, config: RunnableConfig):
        """Initialize the file path for the local memory."""

        folder_path, file_path = self._get_path(config)

        if not folder_path.exists():
            folder_path.mkdir(parents=True, exist_ok=True)
        
        if not file_path.exists():
            file_path.touch()
            file_path.write_text(
                json.dumps([], ensure_ascii=self.ensure_ascii), encoding=self.encoding
            )

        return folder_path, file_path

    def load_messages(self, config: RunnableConfig) -> List[BaseMessage]:
        """Retrieve the messages from the local file"""

        _, file_path = self._get_path(config)
        # items = json.loads(file_path.read_text(encoding=self.encoding))
        with open(str(file_path), 'r', encoding=self.encoding) as f:
            items = json.load(f)
        messages = self.convert_to_base_messages(items)
        return messages

    def convert_to_base_messages(self, items) -> List[BaseMessage]:
        """Load messages from the local file"""
        messages = []
        for message in items:
            if message["role"] == "human":
                messages.append(HumanMessage(
                    id=message["message_id"],
                    content=message["content"]
                ))
            elif message["role"] == "ai":
                messages.append(AIMessage(
                    id=message["message_id"],
                    content=message["content"]
                ))
            else:
                logger.warning(f"Unknown message role `{message['role']}` in local memory, skipping.")
                continue
        return messages[:self.memory_length]
    
    def add_message(
        self,
        message: BaseMessage,
        config: RunnableConfig
    ) -> None:
        """Append the message to the record in the local file"""

        new_message = Message(
            message_id=message.id,
            user_id=get_user_id(config),
            session_id=get_session_id(config),
            role=message.type,
            content=message.content,
        )


        _, file_path = self._init_path(config)

        messages = json.loads(file_path.read_text(encoding=self.encoding))
        mapping_messages = {msg["message_id"]: msg for msg in messages}

        mapping_messages[new_message.message_id] = new_message.model_dump()

        try:
            file_path.write_text(
                json.dumps(
                    list(mapping_messages.values()),
                    ensure_ascii=self.ensure_ascii,
                    indent=2
                ),
                encoding=self.encoding
            )
            logger.success(f"Successfully added message `{message.content[:20] + '...' if len(message.content) > 20 else message.content}` to local file: {file_path}")
        except Exception as e:
            logger.exception(f"Failed to add message to local file {file_path}: {e}")

    def clear(self) -> None:
        """Clear session memory from the local file"""
        try:
            self.file_path.write_text(
                json.dumps([], ensure_ascii=self.ensure_ascii), encoding=self.encoding
            )
            logger.success(f"Cleared session memory in local file: {self.file_path}")
        except Exception as e:
            logger.exception(f"Failed to clear session memory in local file {self.file_path}: {e}")


local_memory_manager = LocalMemory(memory_length=configs.memory_length)