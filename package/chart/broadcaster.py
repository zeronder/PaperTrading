import json
from queue import Queue
from threading import Lock


class ChartBroadcaster:

    def __init__(self):

        self.clients = []

        self.lock = Lock()

    # ========================================================
    # Subscribe browser client
    # ========================================================

    def subscribe(self):

        queue = Queue()

        with self.lock:

            self.clients.append(queue)

            client_count = len(
                self.clients
            )

        return queue

    # ========================================================
    # Remove browser client
    # ========================================================

    def unsubscribe(self, queue):

        with self.lock:

            if queue in self.clients:

                self.clients.remove(queue)

    # ========================================================
    # Broadcast candle
    # ========================================================

    def publish(
        self,
        event_type,
        candle,
    ):

        if candle is None:

            return

        try:

            timestamp = int(
                candle.timestamp.timestamp()
            )

            data = {
                "type": event_type,

                "candle": {
                    "time": timestamp,

                    "open": float(
                        candle.open
                    ),

                    "high": float(
                        candle.high
                    ),

                    "low": float(
                        candle.low
                    ),

                    "close": float(
                        candle.close
                    ),

                    "volume": int(
                        candle.volume
                    ),
                },
            }

            # ------------------------------------------------
            # Proper SSE event
            # ------------------------------------------------

            message = (
                f"event: candle\n"
                f"data: {json.dumps(data)}\n\n"
            )

        except Exception:

            return

        # ----------------------------------------------------
        # Copy clients while holding lock
        # ----------------------------------------------------

        with self.lock:

            clients = list(
                self.clients
            )

        # ----------------------------------------------------
        # Send to every browser
        # ----------------------------------------------------

        for queue in clients:

            try:

                queue.put_nowait(
                    message
                )

            except Exception:

                pass

    # ========================================================
    # Heartbeat
    # ========================================================

    def heartbeat(self, queue):

        try:

            queue.put_nowait(
                ": heartbeat\n\n"
            )

        except Exception:

            pass

    # ========================================================
    # Number of connected charts
    # ========================================================

    def client_count(self):

        with self.lock:

            return len(
                self.clients
            )