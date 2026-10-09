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