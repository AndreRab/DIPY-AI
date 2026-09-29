from dataclasses import dataclass
from abc import ABC, abstractmethod
import pandas as pd

@dataclass(frozen=True)
class SimulatorState():
    """State of the simulator at a given time step."""
    diffrence_x : float 
    diffrence_y : float
    diffrence_laser_power : float
    diffrence_scan_speed : float


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