from dataclasses import dataclass
from abc import ABC, abstractmethod

@dataclass(frozen=True)
class SimulatorState():
    pass  # Placeholder for state attributes

class BaseSimulator(ABC):
    @abstractmethod
    def step(self) -> SimulatorState:
        """Advance the process by one simulation step."""
        ...

    @abstractmethod
    def get_current_state(self) -> SimulatorState:
        ...

    @abstractmethod
    def get_recent_states(self, n: int) -> list[SimulatorState]:
        ...