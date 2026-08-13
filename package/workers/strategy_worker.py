from queue import Queue, Empty
from threading import Event

from package.logger import get_logger


class StrategyWorker:

    def __init__(
        self,
        queue: Queue,
        stop_event: Event,
    ):
        self.queue = queue
        self.stop_event = stop_event

        self.logger = get_logger(__name__)

    def run(self):

        self.logger.info(
            "Strategy worker started"
        )

        while not self.stop_event.is_set():

            try:
                tick = self.queue.get(
                    timeout=0.5
                )

            except Empty:
                continue

            try:

                self.logger.debug(
                    f"Strategy received tick: {tick.token}"
                )

                self.process_tick(tick)

            except Exception:

                self.logger.exception(
                    "Strategy processing failed"
                )

            finally:

                self.queue.task_done()

        self.logger.info(
            "Strategy worker stopped"
        )

    def process_tick(self, tick):
        pass