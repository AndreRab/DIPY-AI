from dipy_ai.tools import BaseTool
from dipy_ai.simulation import SimulatorState
from dipy_ai.simulation.state_provider import SimulationStateProvider

class CurrentStateTool(BaseTool):
    def __init__(self, 
                state_provider: SimulationStateProvider,
                name: str = "Current State Tool", 
                description: str = "A tool for retrieving the current state of the simulation."):
        super().__init__(name, description)
        self._state_provider = state_provider

    def execute(self, *args, **kwargs) -> SimulatorState | None:
        return self._state_provider.get_current_state()