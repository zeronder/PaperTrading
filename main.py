import threading
from queue import Queue, Full

from package import Client
from package.logger import setup_logging, get_logger

from package.workers import (
    DatabaseWorker,
    StrategyWorker,
    CandleWorker,
)

from package.websocket_manager import WebSocketManager

from package.market_data import CandleStore

from package.chart import create_chart_server

from package.chart.broadcaster import (
    ChartBroadcaster,
)


# ============================================================
# Logging
# ============================================================

setup_logging()

logger = get_logger(__name__)


# ============================================================
# Global Stop Event
# ============================================================

stop_event = threading.Event()


# ============================================================
# Queues
# ============================================================

strategy_queue = Queue(
    maxsize=1000
)

database_queue = Queue(
    maxsize=1000
)

candle_queue = Queue(
    maxsize=1000
)


# ============================================================
# Candle Store
# ============================================================

candle_store = CandleStore(
    max_candles=500
)


# ============================================================
# Chart Broadcaster
# ============================================================

chart_broadcaster = ChartBroadcaster()


# ============================================================
# Workers
# ============================================================

database_worker = DatabaseWorker(
    database_queue,
    stop_event,
)

strategy_worker = StrategyWorker(
    strategy_queue,
    stop_event,
)

candle_worker = CandleWorker(
    queue=candle_queue,
    stop_event=stop_event,
    candle_store=candle_store,
    timeframe_seconds=60,
    chart_broadcaster=chart_broadcaster,
)


# ============================================================
# Tick Dispatcher
# ============================================================

def dispatch_tick(tick):

    # --------------------------------------------------------
    # Strategy Queue
    # --------------------------------------------------------

    try:

        strategy_queue.put_nowait(
            tick
        )

    except Full:

        logger.error(
            f"Strategy queue full | "
            f"token={tick.token}"
        )

    # --------------------------------------------------------
    # Database Queue
    # --------------------------------------------------------

    try:

        database_queue.put_nowait(
            tick
        )

    except Full:

        logger.error(
            f"Database queue full | "
            f"token={tick.token}"
        )

    # --------------------------------------------------------
    # Candle Queue
    # --------------------------------------------------------

    try:

        candle_queue.put_nowait(
            tick
        )

    except Full:

        logger.error(
            f"Candle queue full | "
            f"token={tick.token}"
        )

    # --------------------------------------------------------
    # Queue Status
    # --------------------------------------------------------

    logger.debug(
        f"Queue size | "
        f"strategy={strategy_queue.qsize()} "
        f"database={database_queue.qsize()} "
        f"candle={candle_queue.qsize()}"
    )


# ============================================================
# Main
# ============================================================

def main():

    logger.info(
        "Paper Trading application started"
    )

    # ========================================================
    # Workers
    # ========================================================

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

    candle_thread = threading.Thread(
        target=candle_worker.run,
        daemon=True,
        name="CandleWorker",
    )

    # --------------------------------------------------------
    # Start Workers
    # --------------------------------------------------------

    database_thread.start()

    strategy_thread.start()

    candle_thread.start()

    # ========================================================
    # Chart Server
    # ========================================================

    chart_app = create_chart_server(
        candle_store=candle_store,
        chart_broadcaster=chart_broadcaster,
    )

    chart_thread = threading.Thread(
        target=lambda: chart_app.run(
            host="127.0.0.1",
            port=5000,
            debug=False,
            use_reloader=False,
            threaded=True,
        ),
        daemon=True,
        name="ChartServer",
    )

    chart_thread.start()

    logger.info(
        "Chart server started at "
        "http://127.0.0.1:5000"
    )

    # ========================================================
    # Login
    # ========================================================

    client = Client()

    client.login()

    logger.info(
        "Login successful"
    )

    # ========================================================
    # WebSocket
    # ========================================================

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

    # ========================================================
    # Wait
    # ========================================================

    try:

        ws_thread.join()

    except KeyboardInterrupt:

        logger.info(
            "Shutdown requested"
        )

        stop_event.set()

        logger.info(
            "Waiting for workers to stop..."
        )

        database_thread.join()

        strategy_thread.join()

        candle_thread.join()

        chart_thread.join(
            timeout=2
        )

        logger.info(
            "Paper Trading Application Stopped"
        )


# ============================================================
# Entry Point
# ============================================================

if __name__ == "__main__":

    main()
