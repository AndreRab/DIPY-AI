import math
from collections.abc import Mapping

from dipy_ai.tools import BaseTool
from dipy_ai.simulation import BaseSimulator


class AnomalyTool(BaseTool):
    def __init__(self, 
                simulator: BaseSimulator,
                thresholds: Mapping[str, float] | None = None,
                name: str = "Anomaly Tool", 
                description: str = "A tool for detecting anomalies in the data."):
        super().__init__(name, description)
        self._simulator = simulator
        self._thresholds = dict(thresholds or {})

        valid_thresholds = {"x_position", "y_position", "laser_power", "scan_speed"}
        unknown_thresholds = self._thresholds.keys() - valid_thresholds
        if unknown_thresholds:
            raise ValueError(f"Unknown anomaly threshold names: {sorted(unknown_thresholds)}")
        for name, threshold in self._thresholds.items():
            if (
                isinstance(threshold, bool)
                or not isinstance(threshold, (int, float))
                or not math.isfinite(threshold)
                or threshold < 0
            ):
                raise ValueError(f"Threshold for {name!r} must be a finite, non-negative number")
            self._thresholds[name] = float(threshold)

    def execute(self, **kwargs) -> dict:
        state = self._simulator.get_current_state()
        if state is None:
            return {"status": "no_data", "metrics": []}

        signals = (
            ("x_position", "x_position_mm", "mm"),
            ("y_position", "y_position_mm", "mm"),
            ("laser_power", "laser_power_w", "W"),
            ("scan_speed", "scan_speed_mm_s", "mm/s"),
        )
        metrics = []

        for name, value_field, unit in signals:
            values = getattr(state, value_field, None)
            command_value = getattr(values, "command", None)
            measured_value = getattr(values, "measured", None)
            threshold = self._thresholds.get(name)
            difference = None
            absolute_difference = None

            if command_value is None or measured_value is None:
                status = "not_evaluated"
                reason = "missing_measurement"
            else:
                difference = command_value - measured_value
                absolute_difference = abs(difference)
                if threshold is None:
                    status = "not_evaluated"
                    reason = "threshold_not_configured"
                elif absolute_difference > threshold:
                    status = "anomaly"
                    reason = None
                else:
                    status = "normal"
                    reason = None

            metrics.append({
                "name": name,
                "command_value": command_value,
                "measured_value": measured_value,
                "difference": difference,
                "absolute_difference": absolute_difference,
                "unit": unit,
                "threshold_abs": threshold,
                "status": status,
                "reason": reason,
            })

        statuses = [metric["status"] for metric in metrics]
        if "anomaly" in statuses:
            overall_status = "anomaly"
        elif all(status == "normal" for status in statuses):
            overall_status = "normal"
        elif any(status in {"normal", "anomaly"} for status in statuses):
            overall_status = "partially_evaluated"
        else:
            overall_status = "not_evaluated"

        return {
            "status": overall_status,
            "thresholds_configured": bool(self._thresholds),
            "difference_definition": "command_value - measured_value",
            "metrics": metrics,
        }
