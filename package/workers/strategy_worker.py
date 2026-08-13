from queue import Queue

from package.logger import get_logger


class StrategyWorker:

    def __init__(self, queue: Queue):

        self.queue = queue
        self.logger = get_logger(__name__)

    def run(self):

        self.logger.info("Strategy worker started")

        while True:

            tick = self.queue.get()

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

    def process_tick(self, tick):

        # Future:
        #
        # signal = strategy.process(tick)
        #
        # if signal:
        #     order_manager.execute(signal)

        pass
    