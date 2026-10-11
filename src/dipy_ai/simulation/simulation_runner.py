import threading

from dipy_ai.simulation.base_simulator import BaseSimulator


class SimulationRunner:
    def __init__(self, simulator: BaseSimulator, interval_ms: int = 1000):
        self.simulator = simulator
        self.set_interval(interval_ms)
        self._stop_event = threading.Event()
        self._thread = None

    def set_interval(self, interval_ms: int):
        self._interval_ms = interval_ms

    @property
    def running(self):
        return bool(self._thread and self._thread.is_alive() and not self._stop_event.is_set())

    def start(self):
        if self.running:
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self):
        try:
            while not self._stop_event.is_set():
                self.simulator.step()
                self._stop_event.wait(self._interval_ms / 1000)
        finally:
            self._stop_event.set()

    def stop(self):
        self._stop_event.set()
        if self._thread and self._thread is not threading.current_thread():
            self._thread.join()
