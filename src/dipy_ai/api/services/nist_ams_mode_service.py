"""API operations composed from an existing runner and corruption simulator."""
from dataclasses import asdict
from threading import Lock
from uuid import uuid4

from dipy_ai.simulation.nis_ams_100_69_simulator.nist_ams_100_69_corrupt_mode_simulator import (
    CORRUPTION_MODE,
    NIST_AMS_100_69_CorruptModeSimulator,
)
from dipy_ai.simulation.simulation_runner import SimulationRunner


class NIST_AMS_SumulationService:
    def __init__(
        self,
        runner: SimulationRunner,
        simulator: NIST_AMS_100_69_CorruptModeSimulator,
        seed: int = 42,
    ):
        if runner.simulator is not simulator:
            raise ValueError("Runner and service must use the same simulator")
        self.runner = runner
        self.simulator = simulator
        self.seed = seed
        self.mode: str | None = None
        self.interval_ms = runner._interval_ms
        self._lock = Lock()
        self.run_id: str | None = None
        self._step_number = 0
        self._segment = 0
        self._cursor: tuple[int, int] | None = None
        self._observed: dict[int, tuple[object, int, int]] = {}

    @staticmethod
    def available_modes() -> list[dict[str, str]]:
        labels = {
            CORRUPTION_MODE.CLEAN: "Clean",
            CORRUPTION_MODE.LASER_REDUCE_SENSOR_ONLY: "Laser power sensor reduction",
            CORRUPTION_MODE.LASER_REDUCE_SENSOR_AND_MELT_POOL: "Laser power and melt pool reduction",
            CORRUPTION_MODE.LASER_FAILERE: "Laser failure",
            CORRUPTION_MODE.POSSITION_NOISE: "Position noise",
        }
        return [{"id": mode.value, "label": labels[mode]} for mode in CORRUPTION_MODE]

    @staticmethod
    def _validate_interval(interval_ms: int):
        if isinstance(interval_ms, bool) or not isinstance(interval_ms, int) or not 50 <= interval_ms <= 2000:
            raise ValueError("Step interval must be an integer between 50 and 2000 ms")

    def start(self, mode: CORRUPTION_MODE | str, interval_ms: int = 1000) -> dict:
        """Start a fresh simulator with the selected mode and interval."""
        mode = CORRUPTION_MODE(mode)
        self._validate_interval(interval_ms)
        with self._lock:
            # Construct first so invalid data does not stop the current run.
            simulator = type(self.simulator)(
                data_folder=self.simulator.data_folder,
                corruption_mode=mode,
                seed=self.seed,
            )
            self.runner.stop()
            self.simulator.data.close()
            self.simulator = simulator
            self.runner.simulator = simulator
            self.run_id = str(uuid4())
            self._step_number = 0
            self._segment = 0
            self._cursor = None
            self._observed.clear()
            self.mode = mode.value
            self.interval_ms = interval_ms
            self.runner.set_interval(interval_ms)
            self.runner.start()
            return self._snapshot()

    def stop(self) -> dict:
        with self._lock:
            self.runner.stop()
            return self._snapshot()

    def resume(self, interval_ms: int | None = None) -> dict:
        if interval_ms is not None:
            self._validate_interval(interval_ms)
        with self._lock:
            if self.mode is None:
                raise ValueError("Start a simulation before resuming")
            if not self.runner.running:
                if interval_ms is not None:
                    self.interval_ms = interval_ms
                    self.runner.set_interval(interval_ms)
                self.runner.start()
            return self._snapshot()

    def get_current_state(self):
        with self._lock:
            return self.simulator.get_current_state()

    def get_recent_states(self, n: int = 100):
        with self._lock:
            return self.simulator.get_recent_states(n)

    def snapshot(self) -> dict:
        with self._lock:
            return self._snapshot()

    def _snapshot(self) -> dict:
        # Keep UI identifiers stable while reading the simulator's bounded history.
        states = self.simulator.get_recent_states(100)
        cursor = (self.simulator.data_file_index, self.simulator.data_current_record_index)
        if self._cursor is not None and (cursor[0] != self._cursor[0] or cursor[1] < self._cursor[1]):
            self._segment += 1
        previous = self._observed
        self._observed = {}
        rows = []
        for state in states:
            identity = id(state)
            if identity in previous and previous[identity][0] is state:
                record = previous[identity]
            else:
                self._step_number += 1
                record = (state, self._step_number, self._segment)
            self._observed[identity] = record
            rows.append({"step": record[1], "segment": record[2], "values": asdict(state)})
        self._cursor = cursor
        state = states[-1] if states else None
        return {
            "run_id": self.run_id,
            "mode": self.mode,
            "interval_ms": self.interval_ms,
            "running": self.runner.running,
            "error": None,
            "current_state": asdict(state) if state is not None else None,
            "states": rows,
        }

    def close(self):
        with self._lock:
            self.runner.stop()
            self.simulator.data.close()
