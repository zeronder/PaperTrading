from datetime import datetime

from package.market_data.candle import Candle


class CandleBuilder:

    def __init__(self, timeframe_seconds=60):

        self.timeframe_seconds = timeframe_seconds
        self.current_candle = None

    def update(self, tick):

        # --------------------------------
        # Validate price
        # --------------------------------

        price = tick.last_traded_price

        if price is None:
            return None

        # --------------------------------
        # Validate timestamp
        # --------------------------------

        timestamp = tick.exchange_timestamp

        if timestamp is None:
            return None

        # SmartAPI timestamp = milliseconds
        timestamp = datetime.fromtimestamp(
            timestamp / 1000
        )

        # --------------------------------
        # 1-minute bucket
        # --------------------------------

        candle_timestamp = timestamp.replace(
            second=0,
            microsecond=0
        )

        # =================================
        # FIRST TICK
        # =================================

        if self.current_candle is None:

            self.current_candle = Candle(
                timestamp=candle_timestamp,
                open=price,
                high=price,
                low=price,
                close=price,
            )

            return {
                "type": "new",
                "candle": self.current_candle,
            }

        # =================================
        # SAME 1-MINUTE CANDLE
        # =================================

        if candle_timestamp == self.current_candle.timestamp:

            self.current_candle.high = max(
                self.current_candle.high,
                price
            )

            self.current_candle.low = min(
                self.current_candle.low,
                price
            )

            self.current_candle.close = price

            return {
                "type": "update",
                "candle": self.current_candle,
            }

        # =================================
        # NEW MINUTE
        # =================================

        completed_candle = self.current_candle

        self.current_candle = Candle(
            timestamp=candle_timestamp,
            open=price,
            high=price,
            low=price,
            close=price,
        )

        return {
            "type": "closed",
            "candle": completed_candle,
            "new_candle": self.current_candle,
        }