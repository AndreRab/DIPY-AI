from dipy_ai.simulation import BaseSimulator, SimulatorState

class NIST_AMS_100_69_SimulatorState(SimulatorState):
    pass

class NIST_AMS_100_69_Simulator(BaseSimulator):
    def __init__(self):
        super().__init__()
        
    def step(self):
        return None
    
    def get_current_SimulatorState(self):
        return None
    
    def get_recent_SimulatorStates(self, n: int):
        return []