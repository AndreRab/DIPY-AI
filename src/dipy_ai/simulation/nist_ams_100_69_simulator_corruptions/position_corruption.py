from dataclasses import replace

from dipy_ai.simulation.nist_ams_100_69_simulator import NIST_AMS_100_69_SimulatorState
from dipy_ai.simulation.nist_ams_100_69_simulator_corruptions.base_corruption import BaseCorruption

class PositionCorruption(BaseCorruption):
    def __init__(self, magnitude: float = 0.1):
        self.magnitude = magnitude

    def apply(self, state: NIST_AMS_100_69_SimulatorState) -> NIST_AMS_100_69_SimulatorState:
        x_position_mm = state.x_position_mm
        if x_position_mm.measured is not None:
            x_position_mm = replace(x_position_mm, measured=x_position_mm.measured * (1 + self.magnitude))
        y_position_mm = state.y_position_mm
        if y_position_mm.measured is not None:
            y_position_mm = replace(y_position_mm, measured=y_position_mm.measured * (1 + self.magnitude))
        return replace(
            state,
            x_position_mm=x_position_mm,
            y_position_mm=y_position_mm,
        )
