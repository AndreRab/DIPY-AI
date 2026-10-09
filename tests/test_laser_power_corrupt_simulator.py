import tempfile
import unittest
from pathlib import Path

from dipy_ai.simulation import SIMULATORS_MAP
from dipy_ai.simulation.nist_ams_100_69_simulator import COLUMN_NAMES
from dipy_ai.simulation.nist_ams_100_69_laser_power_corrupt_simulator import (
    NIST_AMS_100_69_LaserPowerCorruptSimulator as Simulator,
)


class LaserPowerCorruptionTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.path = Path(self.folder.name, 'data.csv')
        self.path.write_text(','.join('100' for _ in COLUMN_NAMES) + '\n')

    def make(self, **kwargs):
        sim = Simulator(self.folder.name, **kwargs)
        self.addCleanup(lambda: sim.data.close())
        return sim

    def test_sensor_only(self):
        sim = self.make()
        state = sim.step()
        self.assertEqual(state.laser_power_w.measured, 50)
        self.assertEqual(state.laser_power_w.command, 100)
        self.assertEqual(state.melt_pool_length_t100_mm, 100)
        self.assertEqual(state.melt_pool_area_t80_mm2, 100)

    def test_coupled_factors_and_no_accumulation(self):
        sim = self.make(mode='sensor_and_melt_pool')
        for _ in range(3):
            state = sim.step()
            self.assertEqual(state.laser_power_w.measured, 50)
            self.assertEqual(state.laser_power_w.command, 100)
            self.assertEqual(state.melt_pool_length_t100_mm, 75)
            self.assertEqual(state.melt_pool_width_t100_mm, 75)
            for name in ('melt_pool_area_t80_mm2', 'melt_pool_area_t100_mm2',
                         'melt_pool_area_t120_mm2'):
                self.assertEqual(getattr(state, name), 56.25)
            self.assertEqual(state.scan_speed_mm_s.measured, 100)
            self.assertEqual(state.x_position_mm.measured, 100)
            self.assertIs(sim.get_current_state(), state)
            self.assertIs(sim.get_recent_states(1)[0], state)

    def test_missing_values(self):
        self.path.write_text(','.join('' for _ in COLUMN_NAMES) + '\n')
        state = self.make(mode='sensor_and_melt_pool').step()
        self.assertIsNone(state.laser_power_w.measured)
        self.assertIsNone(state.melt_pool_length_t100_mm)
        self.assertIsNone(state.melt_pool_area_t100_mm2)

    def test_validation_and_registration(self):
        self.assertIs(SIMULATORS_MAP['nist_ams_100_69_laser_power_corrupt'], Simulator)
        for kwargs in ({'mode': 'unknown'}, {'magnitude': -2}, {'magnitude': 0.5},
                       {'magnitude': float('nan')}):
            with self.assertRaises(ValueError):
                self.make(**kwargs)
