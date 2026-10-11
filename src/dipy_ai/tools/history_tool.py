from dipy_ai.tools import BaseTool
from dipy_ai.simulation import SimulatorState
from dipy_ai.simulation.state_provider import SimulationStateProvider

class HistoryTool(BaseTool):
    def __init__(self, 
                state_provider: SimulationStateProvider,
                name: str = "History Tool", 
                description: str = "A tool for retrieving the history of the simulation."):
        super().__init__(name, description)
        self._state_provider = state_provider

    def execute(self, *args, **kwargs) -> list[SimulatorState]:
        return list(self._state_provider.get_recent_states(n=kwargs.get("n", 10)))