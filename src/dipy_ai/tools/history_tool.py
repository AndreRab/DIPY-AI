from dipy_ai.tools import BaseTool
from dipy_ai.simulation import BaseSimulator, SimulatorState

class HistoryTool(BaseTool):
    def __init__(self, 
                simulator: BaseSimulator,
                name: str = "History Tool", 
                description: str = "A tool for retrieving the history of the simulation."):
        super().__init__(name, description)
        self._simulator = simulator

    def execute(self, *args, **kwargs) -> list[SimulatorState]:
        return self._simulator.get_recent_states(n=kwargs.get("n", 10))