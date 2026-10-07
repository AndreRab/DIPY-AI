from dipy_ai.simulation.nist_ams_100_69_simulator_corruptions.base_corruption import BaseCorruption
from dipy_ai.simulation.nist_ams_100_69_simulator_corruptions.laser_power_corruption import LaserPowerCorruption
from dipy_ai.simulation.nist_ams_100_69_simulator_corruptions.position_corruption import PositionCorruption
from dipy_ai.simulation.nist_ams_100_69_simulator_corruptions.scan_speed_corruption import ScanSpeedCorruption
from dipy_ai.simulation.nist_ams_100_69_simulator_corruptions.melt_pool_length_t100_corruption import MeltPoolLengthT100Corruption
from dipy_ai.simulation.nist_ams_100_69_simulator_corruptions.melt_pool_width_t100_corruption import MeltPoolWidthT100Corruption
from dipy_ai.simulation.nist_ams_100_69_simulator_corruptions.melt_pool_area_t80_corruption import MeltPoolAreaT80Corruption
from dipy_ai.simulation.nist_ams_100_69_simulator_corruptions.melt_pool_area_t100_corruption import MeltPoolAreaT100Corruption
from dipy_ai.simulation.nist_ams_100_69_simulator_corruptions.melt_pool_area_t120_corruption import MeltPoolAreaT120Corruption

from enum import Enum

class CorruprionType(Enum):
    POSITION = "position"
    LASER_POWER = "laser_power"
    SCAN_SPEED = "scan_speed"
    MELT_POOL_LENGTH_T100 = "melt_pool_length_t100"
    MELT_POOL_WIDTH_T100 = "melt_pool_width_t100"
    MELT_POOL_AREA_T80 = "melt_pool_area_t80"
    MELT_POOL_AREA_T100 = "melt_pool_area_t100"
    MELT_POOL_AREA_T120 = "melt_pool_area_t120"
    
CorruptionTypeToClassMap = {
    CorruprionType.POSITION: PositionCorruption,
    CorruprionType.LASER_POWER: LaserPowerCorruption,
    CorruprionType.SCAN_SPEED: ScanSpeedCorruption,
    CorruprionType.MELT_POOL_LENGTH_T100: MeltPoolLengthT100Corruption,
    CorruprionType.MELT_POOL_WIDTH_T100: MeltPoolWidthT100Corruption,
    CorruprionType.MELT_POOL_AREA_T80: MeltPoolAreaT80Corruption,
    CorruprionType.MELT_POOL_AREA_T100: MeltPoolAreaT100Corruption,
    CorruprionType.MELT_POOL_AREA_T120: MeltPoolAreaT120Corruption,
}