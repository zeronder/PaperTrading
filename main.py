import threading
from queue import Queue

from package import Client
from package.logger import setup_logging, get_logger

from package.workers import (
    DatabaseWorker,
    StrategyWorker,
)

from package.websocket_manager import WebSocketManager


setup_logging()

logger = get_logger(__name__)

stop_event = threading.Event()

strategy_queue = Queue(maxsize=1000)
database_queue = Queue(maxsize=1000)


database_worker = DatabaseWorker(
    database_queue, stop_event
)

strategy_worker = StrategyWorker(
    strategy_queue, stop_event
)


def dispatch_tick(tick):

    strategy_queue.put(tick)
    database_queue.put(tick)

    logger.debug(
        f"Queue size | "
        f"strategy={strategy_queue.qsize()} "
        f"database={database_queue.qsize()}"
    )


def main():

    logger.info(
        "Paper Trading application started"
    )

    # ---------------- Workers ----------------

    database_thread = threading.Thread(
        target=database_worker.run,
        daemon=True,
        name="DatabaseWorker",
    )

    strategy_thread = threading.Thread(
        target=strategy_worker.run,
        daemon=True,
        name="StrategyWorker",
    )

    database_thread.start()
    strategy_thread.start()

    # ---------------- Login ----------------

    client = Client()

    client.login()

    logger.info(
        "Login successful"
    )

    # ---------------- WebSocket ----------------

    websocket_manager = WebSocketManager(
        client=client,
        tick_handler=dispatch_tick,
    )

    ws_thread = threading.Thread(
        target=websocket_manager.start,
        daemon=True,
        name="WebSocketWorker",
    )

    ws_thread.start()

    logger.info(
        "Paper Trading System is running"
    )

    try:

        ws_thread.join()

    except KeyboardInterrupt:

        logger.info(
            "Shutdown requested"
        )

        stop_event.set()

        logger.info("Waiting for workers to stop...")

        database_thread.join()
        strategy_thread.join()

        logger.info("Paper Trading Application Stopped")

if __name__ == "__main__":
    main()