from abc import ABC
from dataclasses import dataclass

@dataclass(frozen=True)
class UserMessage:
    message: str

class BaseAgent(ABC):
    def __init__(self, agent_name: str = 'BaseAgent'):
        self.agent_name = agent_name

    def handle_message(self, message: str) -> str:
        raise NotImplementedError("Subclasses must implement this method.")
    
    def __str__(self):
        return self.agent_name
    