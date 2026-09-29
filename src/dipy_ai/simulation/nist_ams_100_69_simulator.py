from dipy_ai.simulation import BaseSimulator, SimulatorState

class NIST_AMS_100_69_SimulatorState(SimulatorState):
    pass

class NIST_AMS_100_69_Simulator(BaseSimulator):
    def __init__(self):
        super().__init__()
        
    def step(self):
        return None
    
    def get_current_state(self):
        return None
    
    def get_recent_states(self, n: int):
        return []