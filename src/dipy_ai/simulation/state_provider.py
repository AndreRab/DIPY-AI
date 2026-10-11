"""Read-only state contract for tools, independent of API services."""
from collections.abc import Sequence
from typing import Protocol

from dipy_ai.simulation.base_simulator import SimulatorState


class SimulationStateProvider(Protocol):
    """Provide current telemetry and history without exposing run controls."""

    def get_current_state(self) -> SimulatorState | None:
        ...

    def get_recent_states(self, n: int) -> Sequence[SimulatorState]:
        ...
