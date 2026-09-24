import threading
import time

from dipy_ai.simulation import BaseSimulator
from dipy_ai.agent import BaseAgent

class SimulationRunner:
    def __init__(self, simulator: BaseSimulator, interval_ms: int = 1000):
        self.simulator = simulator
        self._interval_ms = interval_ms
        self._running = False
        self._thread = None

    def start(self):
        self._running = True
        self._thread = threading.Thread(
            target=self._run,
            daemon=True,
        )
        self._thread.start()

    def _run(self):
        while self._running:
            state = self.simulator.step()
            time.sleep(self._interval_ms / 1000)

    def stop(self):
        self._running = False