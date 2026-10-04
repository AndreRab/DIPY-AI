from dataclasses import dataclass
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

@dataclass(frozen=True)
class CommandMeasuredValue:
    command: float | None
    measured: float | None


@dataclass(frozen=True)
class NIST_AMS_100_69_SimulatorState(SimulatorState):
    """Selected raw telemetry values needed for state and anomaly analysis."""

    x_position_mm: CommandMeasuredValue
    y_position_mm: CommandMeasuredValue
    laser_power_w: CommandMeasuredValue
    scan_speed_mm_s: CommandMeasuredValue
    melt_pool_length_t100_mm: float | None
    melt_pool_width_t100_mm: float | None
    melt_pool_area_t80_mm2: float | None
    melt_pool_area_t100_mm2: float | None
    melt_pool_area_t120_mm2: float | None
        
class NIST_AMS_100_69_Simulator(BaseSimulator):
    def __init__(self, data_folder: str | Path):
        super().__init__()
        self.data_folder = Path(data_folder)
        if not any(self.data_folder.glob("*.csv")):
            raise FileNotFoundError(f"No CSV files found in data folder: {self.data_folder}")
        self.data_current_record_index = 0
        self.data_file_index = 0
        self._recent_states: deque[NIST_AMS_100_69_SimulatorState] = deque(maxlen=100)
        self.data = pd.read_csv(sorted(self.data_folder.glob("*.csv"))[self.data_file_index], names=COLUMN_NAMES, chunksize=1)

    @staticmethod
    def _optional_float(value: object) -> float | None:
        if pd.isna(value):
            return None
        return float(value)

    def step(self) -> NIST_AMS_100_69_SimulatorState:
        try:
            data = next(self.data).iloc[0].to_dict()
        except StopIteration:
            self.data_current_record_index = 0
            self.data_file_index = (self.data_file_index + 1) % len(sorted(self.data_folder.glob("*.csv")))
            self.data = pd.read_csv(sorted(self.data_folder.glob("*.csv"))[self.data_file_index], names=COLUMN_NAMES, chunksize=1)
            data = next(self.data).iloc[0].to_dict()
        self.data_current_record_index += 1

        state = NIST_AMS_100_69_SimulatorState(
            x_position_mm=CommandMeasuredValue(
                command=self._optional_float(data["command_x_mm"]),
                measured=self._optional_float(data["real_x_mm"]),
            ),
            y_position_mm=CommandMeasuredValue(
                command=self._optional_float(data["command_y_mm"]),
                measured=self._optional_float(data["real_y_mm"]),
            ),
            laser_power_w=CommandMeasuredValue(
                command=self._optional_float(data["command_laser_power_w"]),
                measured=self._optional_float(data["real_laser_power_w"]),
            ),
            scan_speed_mm_s=CommandMeasuredValue(
                command=self._optional_float(data["command_scan_speed_mm_s"]),
                measured=self._optional_float(data["real_scan_speed_mm_s"]),
            ),
            melt_pool_length_t100_mm=self._optional_float(data["melt_pool_length_t100_mm"]),
            melt_pool_width_t100_mm=self._optional_float(data["melt_pool_width_t100_mm"]),
            melt_pool_area_t80_mm2=self._optional_float(data["melt_pool_area_t80_mm2"]),
            melt_pool_area_t100_mm2=self._optional_float(data["melt_pool_area_t100_mm2"]),
            melt_pool_area_t120_mm2=self._optional_float(data["melt_pool_area_t120_mm2"]),
        )

        self.current_state = state
        self._recent_states.append(state)
        return state

    def get_current_state(self) -> NIST_AMS_100_69_SimulatorState:
        return self.current_state

    def get_recent_states(self, n: int) -> list[NIST_AMS_100_69_SimulatorState]:
        return list(self._recent_states)[-n:]
