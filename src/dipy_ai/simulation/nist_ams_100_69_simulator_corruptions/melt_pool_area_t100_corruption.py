from dataclasses import replace

from dipy_ai.simulation.nist_ams_100_69_simulator import NIST_AMS_100_69_SimulatorState
from dipy_ai.simulation.nist_ams_100_69_simulator_corruptions.base_corruption import BaseCorruption

class MeltPoolAreaT100Corruption(BaseCorruption):
    def __init__(self, magnitude: float = 0.1):
        self.magnitude = magnitude

    def apply(self, state: NIST_AMS_100_69_SimulatorState) -> NIST_AMS_100_69_SimulatorState:
        melt_pool_area_t100_mm2 = state.melt_pool_area_t100_mm2
        if melt_pool_area_t100_mm2 is not None:
            melt_pool_area_t100_mm2 *= (1 + self.magnitude)
        return replace(
            state,
            melt_pool_area_t100_mm2=melt_pool_area_t100_mm2,
        )
