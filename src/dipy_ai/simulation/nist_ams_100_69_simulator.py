from dipy_ai.simulation import BaseSimulator, SimulatorState
import pandas as pd
from collections import deque
from pathlib import Path



COLUMN_NAMES = [
    "part_number",
    "build_time_us",
    "command_x_mm",
    "command_y_mm",
    "command_laser_power_w",
    "command_scan_speed_mm_s",
    "real_x_mm",
    "real_y_mm",
    "real_laser_power_w",
    "real_scan_speed_mm_s",
    "melt_pool_length_t80_mm",
    "melt_pool_width_t80_mm",
    "melt_pool_area_t80_mm2",
    "melt_pool_length_t100_mm",
    "melt_pool_width_t100_mm",
    "melt_pool_area_t100_mm2",
    "melt_pool_length_t120_mm",
    "melt_pool_width_t120_mm",
    "melt_pool_area_t120_mm2",
    "lwi_powder_led_a_raw",
    "lwi_powder_led_a_mean3",
    "lwi_powder_led_a_mean5",
    "lwi_powder_led_b_raw",
    "lwi_powder_led_b_mean3",
    "lwi_powder_led_b_mean5",
    "lwi_powder_led_c_raw",
    "lwi_powder_led_c_mean3",
    "lwi_powder_led_c_mean5",
    "lwi_exposure_led_a_raw",
    "lwi_exposure_led_a_mean3",
    "lwi_exposure_led_a_mean5",
    "lwi_exposure_led_b_raw",
    "lwi_exposure_led_b_mean3",
    "lwi_exposure_led_b_mean5",
    "lwi_exposure_led_c_raw",
    "lwi_exposure_led_c_mean3",
    "lwi_exposure_led_c_mean5",
    "xct_voxel_raw",
    "xct_voxel_mean3",
    "xct_voxel_mean5",
]
path = Path(__file__).parent.parent.parent.parent/"data"/"AMS_NIST"/"part01"/"L0001.csv"
class NIST_AMS_100_69_SimulatorState(SimulatorState):
    def __init__(self):
        super().__init__()
        self._recent_states : deque[SimulatorState] = deque(maxlen=100)
        self.data = pd.read_csv(path, names=COLUMN_NAMES, chunksize=1)  
        self._current_state : SimulatorState = None

class NIST_AMS_100_69_Simulator(BaseSimulator):
    def __init__(self):
        super().__init__()
        
    def step(self):
        if self._current_state is None:
            self._current_state = next(self.data)
        else:
            self._current_state = next(self.data)
        self._recent_states.append(self._current_state)
        
    
    def get_current_state(self):
        return self._current_state
    
    def get_recent_states(self, n: int):
        return list(self._recent_states)[-n:]