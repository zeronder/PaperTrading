from collections import deque
from threading import Lock


class CandleStore:

    def __init__(self, max_candles=500):

        self.candles = deque(
            maxlen=max_candles
        )

        self.current_candle = None

        self.lock = Lock()

    # ========================================================
    # Add completed candle
    # ========================================================

    def add(self, candle):

        with self.lock:

            self.candles.append(candle)

            self.current_candle = None

    # ========================================================
    # Update current running candle
    # ========================================================

    def update_current(self, candle):

        with self.lock:

            self.current_candle = candle

    # ========================================================
    # Get all completed candles
    # ========================================================

    def get_all(self):

        with self.lock:

            return list(self.candles)

    # ========================================================
    # Get current running candle
    # ========================================================

    def get_current(self):

        with self.lock:

            return self.current_candle

    # ========================================================
    # Get latest candle
    # ========================================================

    def latest(self):

        with self.lock:

            if self.current_candle is not None:

                return self.current_candle

            if not self.candles:

                return None

            return self.candles[-1]