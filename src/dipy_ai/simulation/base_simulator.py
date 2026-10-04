from dataclasses import dataclass
from abc import ABC, abstractmethod

@dataclass(frozen=True)
class SimulatorState():
    """State of the simulator at a given time step."""

class BaseSimulator(ABC):
    """Base class for all simulators."""

    def __init__(self, initial_state: SimulatorState | None = None):
        self.initial_state = initial_state
        self.current_state = initial_state

    @abstractmethod
    def step(self) -> SimulatorState | None:
        """Advance the process by one simulation step."""
        ...

    @abstractmethod
    def get_current_state(self) -> SimulatorState:
        ...

    @abstractmethod
    def get_recent_states(self, n: int) -> list[SimulatorState]:
        ...
