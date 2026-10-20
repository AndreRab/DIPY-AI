from abc import ABC
from dataclasses import dataclass
from typing import Literal, TypedDict


class ChatMessage(TypedDict):
    role: Literal["user", "assistant"]
    content: str

@dataclass(frozen=True)
class UserMessage:
    message: str

class BaseAgent(ABC):
    def __init__(self, agent_name: str = 'BaseAgent'):
        self.agent_name = agent_name

    def handle_message(self, message: UserMessage, history: list[ChatMessage]) -> str:
        raise NotImplementedError("Subclasses must implement this method.")
    
    def __str__(self):
        return self.agent_name
