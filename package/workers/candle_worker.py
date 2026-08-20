from queue import Queue, Empty
from threading import Event

from package.logger import get_logger
from package.market_data import CandleBuilder


class CandleWorker:

    def __init__(
        self,
        queue: Queue,
        stop_event: Event,
        candle_store,
        timeframe_seconds=60,
        chart_broadcaster=None,
    ):

        self.queue = queue
        self.stop_event = stop_event

        self.candle_store = candle_store

        self.candle_builder = CandleBuilder(
            timeframe_seconds=timeframe_seconds
        )

        self.chart_broadcaster = (
            chart_broadcaster
        )

        self.logger = get_logger(
            __name__
        )

        # ====================================================
        # Statistics
        # ====================================================

        self.processed_ticks = 0

        self.new_candles = 0

        self.updated_candles = 0

        self.closed_candles = 0

    # ========================================================
    # Publish candle to chart
    # ========================================================

    def publish_candle(
        self,
        event_type,
        candle,
    ):

        if self.chart_broadcaster is None:

            return

        try:

            self.chart_broadcaster.publish(
                event_type,
                candle,
            )

        except Exception:

            self.logger.exception(
                "Failed to publish candle "
                "to chart"
            )

    # ========================================================
    # Worker
    # ========================================================

    def run(self):

        self.logger.info(
            "Candle worker started"
        )

        while not self.stop_event.is_set():

            try:

                tick = self.queue.get(
                    timeout=0.5
                )

            except Empty:

                continue

            try:

                self.processed_ticks += 1

                result = (
                    self.candle_builder.update(
                        tick
                    )
                )

                if result is not None:

                    candle_type = (
                        result["type"]
                    )

                    candle = (
                        result["candle"]
                    )

                    # ========================================
                    # NEW CANDLE
                    # ========================================

                    if candle_type == "new":

                        self.new_candles += 1

                        self.candle_store.update_current(
                            candle
                        )

                        self.publish_candle(
                            "new",
                            candle,
                        )

                        self.logger.info(
                            f"CANDLE NEW | "
                            f"tick={self.processed_ticks} | "
                            f"time={candle.timestamp} | "
                            f"O={candle.open} | "
                            f"H={candle.high} | "
                            f"L={candle.low} | "
                            f"C={candle.close}"
                        )

                    # ========================================
                    # CURRENT CANDLE UPDATE
                    # ========================================

                    elif candle_type == "update":

                        self.updated_candles += 1

                        self.candle_store.update_current(
                            candle
                        )

                        # ------------------------------------
                        # THIS IS THE IMPORTANT PART
                        # ------------------------------------

                        self.publish_candle(
                            "update",
                            candle,
                        )

                        self.logger.debug(
                            f"CANDLE UPDATE | "
                            f"tick={self.processed_ticks} | "
                            f"time={candle.timestamp} | "
                            f"O={candle.open} | "
                            f"H={candle.high} | "
                            f"L={candle.low} | "
                            f"C={candle.close}"
                        )

                    # ========================================
                    # OLD CANDLE CLOSED
                    # ========================================

                    elif candle_type == "closed":

                        self.closed_candles += 1

                        # ------------------------------------
                        # Store completed candle
                        # ------------------------------------

                        self.candle_store.add(
                            candle
                        )

                        # ------------------------------------
                        # Send completed candle
                        # ------------------------------------

                        self.publish_candle(
                            "closed",
                            candle,
                        )

                        self.logger.info(
                            f"CANDLE CLOSED | "
                            f"tick={self.processed_ticks} | "
                            f"time={candle.timestamp} | "
                            f"O={candle.open} | "
                            f"H={candle.high} | "
                            f"L={candle.low} | "
                            f"C={candle.close}"
                        )

                        # ------------------------------------
                        # New minute candle
                        # ------------------------------------

                        new_candle = (
                            result["new_candle"]
                        )

                        self.new_candles += 1

                        self.candle_store.update_current(
                            new_candle
                        )

                        # ------------------------------------
                        # Send new candle to browser
                        # ------------------------------------

                        self.publish_candle(
                            "new",
                            new_candle,
                        )

                        self.logger.info(
                            f"CANDLE NEW | "
                            f"tick={self.processed_ticks} | "
                            f"time={new_candle.timestamp} | "
                            f"O={new_candle.open} | "
                            f"H={new_candle.high} | "
                            f"L={new_candle.low} | "
                            f"C={new_candle.close}"
                        )

                # ============================================
                # Progress
                # ============================================

                if (
                    self.processed_ticks
                    % 100
                    == 0
                ):

                    self.logger.info(
                        f"CANDLE WORKER PROGRESS | "
                        f"processed={self.processed_ticks} | "
                        f"updates={self.updated_candles} | "
                        f"closed={self.closed_candles}"
                    )

            except Exception:

                self.logger.exception(
                    "Candle processing failed"
                )

            finally:

                self.queue.task_done()

        self.logger.info(
            f"Candle worker stopped | "
            f"processed={self.processed_ticks} | "
            f"updates={self.updated_candles} | "
            f"closed={self.closed_candles}"
        )