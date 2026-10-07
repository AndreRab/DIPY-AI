from dipy_ai.simulation.nist_ams_100_69_simulator_corruptions import (
    CorruprionType, CorruptionTypeToClassMap
)
from dipy_ai.simulation.nist_ams_100_69_simulator import (
    NIST_AMS_100_69_SimulatorState, 
    NIST_AMS_100_69_Simulator
)

from random import Random
from pathlib import Path

        
class NIST_AMS_100_69_CorruptSimulator(NIST_AMS_100_69_Simulator):
    def __init__(self, data_folder: str | Path, 
                 corruption_types: list[CorruprionType] | None = None, 
                 max_corruption_type_num: int = len(CorruprionType),
                 magnitude: float = 0.1,
                 seed: int = 42
                ):
        super().__init__(data_folder)
        if corruption_types is None:
            rng = Random(seed)
            count = rng.randint(1, min(len(CorruprionType), max_corruption_type_num)) if max_corruption_type_num else 0
            corruption_types = rng.sample(list(CorruprionType), k=count)
        self.corruptions = [CorruptionTypeToClassMap[ct](magnitude) for ct in corruption_types]

    def step(self) -> NIST_AMS_100_69_SimulatorState:
        base_state = super().step()
        for corruption in self.corruptions:
            base_state = corruption.apply(base_state)
        self.current_state = base_state
        self._recent_states[-1] = base_state
        return base_state
