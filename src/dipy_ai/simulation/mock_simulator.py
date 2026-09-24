from dipy_ai.simulation import BaseSimulator

class MockSimulator(BaseSimulator):
    def __init__(self):
        super().__init__()
        
    def step(self):
        return None
    
    def get_current_state(self):
        return None
    
    def get_recent_states(self, n: int):
        return []