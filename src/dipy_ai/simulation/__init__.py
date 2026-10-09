from dipy_ai.simulation.base_simulator import BaseSimulator, SimulatorState
from dipy_ai.simulation.mock_simulator import MockSimulator
from dipy_ai.simulation.simulation_runner import SimulationRunner
from dipy_ai.simulation.nist_ams_100_69_simulator import NIST_AMS_100_69_Simulator
from dipy_ai.simulation.nist_ams_100_69_corrupt_mode_simulator import NIST_AMS_100_69_CorruptModeSimulator

SIMULATORS_MAP = {
    "mock": MockSimulator,
    "nist_ams_100_69": NIST_AMS_100_69_Simulator,
    "nist_ams_100_69_corrupt": NIST_AMS_100_69_CorruptModeSimulator
}

def create_simulator(simulator_name: str, data_folder: str, seed: int = 42, corruption_mode: str = None) -> BaseSimulator:
    if simulator_name not in SIMULATORS_MAP:
        raise ValueError(f"Simulator '{simulator_name}' is not supported. Supported simulators: {list(SIMULATORS_MAP.keys())}")
    
    simulator_class = SIMULATORS_MAP[simulator_name]
    
    if simulator_name == "nist_ams_100_69_corrupt":
        if corruption_mode is None:
            raise ValueError("corruption_mode must be provided for 'nist_ams_100_69_corrupt' simulator.")
        return simulator_class(data_folder=data_folder, corruption_mode=corruption_mode, seed=seed)
    
    return simulator_class(data_folder=data_folder, seed=seed)