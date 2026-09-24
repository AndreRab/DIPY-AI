from dataclasses import dataclass
from abc import ABC, abstractmethod

@dataclass(frozen=True)
class State():
    pass  # Placeholder for state attributes

class BaseSimulator(ABC):
    @abstractmethod
    def step(self) -> State:
        """Advance the process by one simulation step."""
        ...

    @abstractmethod
    def get_current_state(self) -> State:
        ...

    @abstractmethod
    def get_recent_states(self, n: int) -> list[State]:
        ...