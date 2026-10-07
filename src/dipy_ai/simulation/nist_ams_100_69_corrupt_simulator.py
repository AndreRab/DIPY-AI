from dipy_ai.simulation.nist_ams_100_69_simulator_corruptions import (
    CorruprionType, CorruptionTypeToClassMap
)
from dipy_ai.simulation.nist_ams_100_69_simulator import (
    NIST_AMS_100_69_SimulatorState, 
    NIST_AMS_100_69_Simulator
)

from random import random
from pathlib import Path

        
class NIST_AMS_100_69_CorruptSimulator(NIST_AMS_100_69_Simulator):
    def __init__(self, data_folder: str | Path, 
                 corruption_types: list[CorruprionType] = None, 
                 max_corruption_type_num: int = len(CorruprionType),
                 magnitude: float = 0.1,
                 seed: int = 42
                ):
        super().__init__(data_folder)
        random.seed(seed)
        corruption_types = random.sample(
            list(CorruprionType),
            k=max(max_corruption_type_num, len(corruption_types) if corruption_types else 0),
        ) if corruption_types is None else corruption_types
        self.corruptions = [CorruptionTypeToClassMap[ct](magnitude) for ct in corruption_types]

    def step(self) -> NIST_AMS_100_69_SimulatorState:
        base_state = super().step()
        for corruption in self.corruptions:
            base_state = corruption.apply(base_state)
        return base_state
    