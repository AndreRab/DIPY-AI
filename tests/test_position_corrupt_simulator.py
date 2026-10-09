import tempfile
import unittest
from pathlib import Path
from random import Random

from dipy_ai.simulation.nist_ams_100_69_simulator import COLUMN_NAMES
from dipy_ai.simulation.nist_ams_100_69_position_corrupt_simulator import (
    NIST_AMS_100_69_PositionCorruptSimulator as Simulator,
)


class PositionCorruptionTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        row = dict.fromkeys(COLUMN_NAMES, '1')
        row.update(real_x_mm='0', real_y_mm='-2')
        line = ','.join(row[name] for name in COLUMN_NAMES)
        Path(self.folder.name, 'data.csv').write_text((line + '\n') * 3)

    def make(self, **kwargs):
        sim = Simulator(self.folder.name, x_offset_mm=2, y_offset_mm=-3, **kwargs)
        self.addCleanup(lambda: sim.data.close())
        return sim

    def test_fixed_does_not_accumulate_even_across_file_wrap(self):
        sim = self.make()
        for _ in range(8):
            state = sim.step()
            self.assertEqual(state.x_position_mm.measured, 2)
            self.assertEqual(state.y_position_mm.measured, -5)
            self.assertEqual(state.x_position_mm.command, 1)
            self.assertEqual(state.laser_power_w.measured, 1)
            self.assertIs(sim.get_current_state(), state)
            self.assertIs(sim.get_recent_states(1)[0], state)

    def test_random_is_seeded_and_per_sample(self):
        sim = self.make(mode='random', seed=7)
        rng = Random(7)
        for _ in range(20):
            apply = rng.random() < 0.5
            state = sim.step()
            self.assertEqual(state.x_position_mm.measured, 2 if apply else 0)
            self.assertEqual(state.y_position_mm.measured, -5 if apply else -2)
            self.assertIs(sim.get_recent_states(1)[0], state)

    def test_probability_boundaries(self):
        for probability in (0, 1):
            sim = self.make(mode='random', corruption_probability=probability)
            self.assertEqual(sim.step().x_position_mm.measured, 2 * probability)

    def test_missing_measurements(self):
        Path(self.folder.name, 'data.csv').write_text(','.join('' for _ in COLUMN_NAMES) + '\n')
        self.assertIsNone(self.make().step().x_position_mm.measured)

    def test_invalid_configuration(self):
        for kwargs in ({'mode': 'drift'}, {'corruption_probability': -1},
                       {'corruption_probability': float('nan')}):
            with self.assertRaises(ValueError):
                self.make(**kwargs)
        with self.assertRaises(ValueError):
            Simulator(self.folder.name, x_offset_mm=float('inf'))
