from dipy_ai.simulation.nist_ams_100_69_simulator import NIST_AMS_100_69_SimulatorState
from dipy_ai.simulation.nist_ams_100_69_simulator_corruptions.base_corruption import BaseCorruption

class ScanSpeedCorruption(BaseCorruption):
    def __init__(self, magnitude: float = 0.1):
        self.magnitude = magnitude

    def apply(self, state: NIST_AMS_100_69_SimulatorState) -> NIST_AMS_100_69_SimulatorState:
        state.scan_speed_mm_s.measured *= (1 + self.magnitude)
        return state