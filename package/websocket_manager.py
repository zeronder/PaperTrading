from package import (
    default_correlation_id,
    default_mode,
    default_token_list,
)

from package.tick import Tick
from package.logger import get_logger


class WebSocketManager:

    def __init__(self, client, tick_handler):

        self.client = client
        self.tick_handler = tick_handler

        self.logger = get_logger(__name__)

        self.sws = None

    def start(self):

        self.sws = self.client.create_sws()

        self.sws.on_open = self.on_open
        self.sws.on_data = self.on_data
        self.sws.on_error = self.on_error
        self.sws.on_close = self.on_close

        self.logger.info(
            "Starting WebSocket"
        )

        self.sws.connect()

    def on_open(self, ws):

        self.logger.info(
            "WebSocket connected"
        )

        self.sws.subscribe(
            default_correlation_id,
            default_mode,
            default_token_list,
        )

        self.logger.info(
            "Subscription sent"
        )

    def on_data(self, ws, message):

        try:

            tick = Tick(message)

            self.tick_handler(tick)

        except Exception:

            self.logger.exception(
                "Error processing tick"
            )

    def on_error(self, ws, error):

        self.logger.error(
            f"WebSocket error: {error}"
        )

    def on_close(self, ws):

        self.logger.warning(
            "WebSocket connection closed"
        )