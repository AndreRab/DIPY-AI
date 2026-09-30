from dataclasses import dataclass
from abc import ABC, abstractmethod
import pandas as pd

@dataclass(frozen=True)
class SimulatorState():
    """State of the simulator at a given time step."""


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