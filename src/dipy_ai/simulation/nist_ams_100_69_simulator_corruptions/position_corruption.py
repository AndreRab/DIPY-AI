from dataclasses import replace

from dipy_ai.simulation.nist_ams_100_69_simulator import NIST_AMS_100_69_SimulatorState
from dipy_ai.simulation.nist_ams_100_69_simulator_corruptions.base_corruption import BaseCorruption

class PositionCorruption(BaseCorruption):
    def __init__(self, 
                magnitude: float = 0.1, 
                offset_x: float = 0.0, 
                offset_y: float = 0.0,
                random_threshold: float = 0.25,
                random_seed: int = 42
        ):
        super().__init__(magnitude, random_seed)
        self.magnitude = magnitude
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.random_threshold = random_threshold

    def apply(self, state: NIST_AMS_100_69_SimulatorState) -> NIST_AMS_100_69_SimulatorState:
        if self.rng.random() > self.random_threshold:
            return state
        x_position_mm = state.x_position_mm
        if x_position_mm.measured is not None:
            x_position_mm = replace(x_position_mm, measured=x_position_mm.measured * (1 + self.magnitude) + self.offset_x)
        y_position_mm = state.y_position_mm
        if y_position_mm.measured is not None:
            y_position_mm = replace(y_position_mm, measured=y_position_mm.measured * (1 + self.magnitude) + self.offset_y)
        return replace(
            state,
            x_position_mm=x_position_mm,
            y_position_mm=y_position_mm,
        )
