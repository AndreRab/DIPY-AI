from random import Random
from dipy_ai.simulation.nist_ams_100_69_simulator import NIST_AMS_100_69_SimulatorState


class BaseCorruption:
    def __init__(self, magnitude: float = 0.1, seed: int = 42):
        self.magnitude = magnitude
        self.rng = Random(seed)
        
    def set_seed(self, seed: int):
        self.rng = Random(seed)

    def apply(self, state: NIST_AMS_100_69_SimulatorState) -> NIST_AMS_100_69_SimulatorState:
        raise NotImplementedError("Subclasses must implement the apply method.")