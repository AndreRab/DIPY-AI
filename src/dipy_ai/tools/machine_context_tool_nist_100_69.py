from dipy_ai.tools import BaseTool

class MachineContext_NIST_AMS_100_69_Tool(BaseTool):
    def __init__(self, 
                name: str = "Machine Context Tool", 
                description: str = "A tool for retrieving the context of the machine."):
        super().__init__(name, description)

    def execute(self, *args, **kwargs) -> str:
        return {
            "machine": {
                "name": "NIST Additive Manufacturing Metrology Testbed (AMMT)",
                "process": "Laser Powder Bed Fusion (LPBF)",
            },
            "build": {
                "name": "Overhang Part X4",
                "parts": 4,
                "layers": 250,
                "layer_thickness_um": 20,
                "scan_orientation": "Alternates 0° and 90° between consecutive layers",
            },
            "material": {
                "powder": "Nickel superalloy 625 (IN625), recycled powder",
                "substrate": "IN625",
            },
            "part": {
                "dimensions_mm": [9, 5, 5],
                "features": [
                    "45° overhang",
                    "horizontal cylindrical cutout",
                ],
            },
            "nominal_process_parameters": {
                "core_laser_power_w": 195,
                "core_scan_speed_mm_s": 800,
                "contour_laser_power_w": 100,
                "contour_scan_speed_mm_s": 900,
                "hatch_spacing_um": 100,
                "laser_spot_size_um": 60,
            },
            "environment": {
                "atmosphere": "Argon",
                "oxygen_ppm": "<500",
                "gas_flow_l_min": 300,
            },
            "monitoring": [
                "XYPT commanded laser position, power and trigger",
                "DAQ measured laser position and laser power",
                "Coaxial melt-pool monitoring camera",
                "Layerwise imaging",
            ],
        }