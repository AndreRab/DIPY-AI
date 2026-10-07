from dataclasses import replace

from dipy_ai.simulation.nist_ams_100_69_simulator import NIST_AMS_100_69_SimulatorState
from dipy_ai.simulation.nist_ams_100_69_simulator_corruptions.base_corruption import BaseCorruption

class LaserPowerCorruption(BaseCorruption):
    def __init__(self, magnitude: float = 0.1):
        self.magnitude = magnitude

    def apply(self, state: NIST_AMS_100_69_SimulatorState) -> NIST_AMS_100_69_SimulatorState:
        laser_power_w = state.laser_power_w
        if laser_power_w.measured is not None:
            laser_power_w = replace(laser_power_w, measured=laser_power_w.measured * (1 + self.magnitude))
        return replace(
            state,
            laser_power_w=laser_power_w,
        )
