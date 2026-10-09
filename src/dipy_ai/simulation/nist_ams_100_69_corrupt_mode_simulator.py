from enum import Enum

from dipy_ai.simulation.nist_ams_100_69_simulator_corruptions import (
    LaserPowerCorruption, 
    MeltPoolLengthT100Corruption,
    MeltPoolWidthT100Corruption,
    MeltPoolAreaT80Corruption,
    MeltPoolAreaT100Corruption,
    MeltPoolAreaT120Corruption,
    PositionCorruption
)
from dipy_ai.simulation.nist_ams_100_69_simulator import (
    NIST_AMS_100_69_SimulatorState, 
    NIST_AMS_100_69_Simulator
)

from random import Random
from pathlib import Path

from dipy_ai.simulation.nist_ams_100_69_simulator_corruptions.base_corruption import BaseCorruption

class CORRUPTION_MODE(Enum):
    LASER_REDUCE_SENSOR_ONLY = "laser_failure_sensor_only"
    LASER_REDUCE_SENSOR_AND_MELT_POOL = "laser_failure_sensor_and_melt_pool"
    LASER_FAILERE = "laser_failure"
    POSSITION_NOISE = "position_noise"

CORRUPTION_MODE_TO_ClASS_MAP = {
    CORRUPTION_MODE.LASER_REDUCE_SENSOR_ONLY: [ 
        LaserPowerCorruption(magnitude=-0.5)
    ],
    CORRUPTION_MODE.LASER_REDUCE_SENSOR_AND_MELT_POOL: [
        LaserPowerCorruption(magnitude=-0.5),
        MeltPoolLengthT100Corruption(magnitude=-0.25),
        MeltPoolWidthT100Corruption(magnitude=-0.25),
        MeltPoolAreaT120Corruption(magnitude=-0.4375),
        MeltPoolAreaT100Corruption(magnitude=-0.4375),
        MeltPoolAreaT80Corruption(magnitude=-0.4375)
    ],
    CORRUPTION_MODE.LASER_FAILERE: [ 
        LaserPowerCorruption(magnitude=-1),
        MeltPoolLengthT100Corruption(magnitude=-1),
        MeltPoolWidthT100Corruption(magnitude=-1),
        MeltPoolAreaT120Corruption(magnitude=-1),
        MeltPoolAreaT100Corruption(magnitude=-1),
        MeltPoolAreaT80Corruption(magnitude=-1)
    ],
    CORRUPTION_MODE.POSSITION_NOISE: [
        PositionCorruption(magnitude=0.0, offset_x=0.034, offset_y=0.106, random_threshold=0.25)
    ]        
}
        
class NIST_AMS_100_69_CorruptModeSimulator(NIST_AMS_100_69_Simulator):
    def __init__(self, data_folder: str | Path, 
                 corruption_mode: CORRUPTION_MODE | str,
                 seed: int = 42
                ):
        super().__init__(data_folder)
        self.corruptions : list[BaseCorruption] = CORRUPTION_MODE_TO_ClASS_MAP[CORRUPTION_MODE(corruption_mode)]
        self._update_seed(seed)
        
    
    def _update_seed(self, seed: int):
        for corruption in self.corruptions:
            corruption.set_seed(seed)

    def step(self) -> NIST_AMS_100_69_SimulatorState:
        base_state = super().step()
        for corruption in self.corruptions:
            base_state = corruption.apply(base_state)
        self.current_state = base_state
        self._recent_states[-1] = base_state
        return base_state
