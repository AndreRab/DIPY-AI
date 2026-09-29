from dipy_ai.tools import BaseTool
from dipy_ai.simulation import BaseSimulator, SimulatorState

class CurrentStateTool(BaseTool):
    def __init__(self, 
                simulator: BaseSimulator,
                name: str = "Current State Tool", 
                description: str = "A tool for retrieving the current state of the simulation."):
        super().__init__(name, description)
        self._simulator = simulator

    def execute(self, *args, **kwargs) -> SimulatorState:
        return self._simulator.get_current_state()