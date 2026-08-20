import threading
from queue import Queue, Full

from package.logger import (
    setup_logging,
    get_logger,
)

from package.workers import (
    StrategyWorker,
    CandleWorker,
)

from package.market_data import CandleStore

from package.chart import (
    create_chart_server,
)

from package.chart.broadcaster import (
    ChartBroadcaster,
)

from package.replay import TickReplay


# ============================================================
# Logging
# ============================================================

setup_logging()

logger = get_logger(
    __name__
)


# ============================================================
# Stop Event
# ============================================================

stop_event = threading.Event()


# ============================================================
# Queues
# ============================================================

strategy_queue = Queue(
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

chart_broadcaster = (
    ChartBroadcaster()
)


# ============================================================
# Workers
# ============================================================

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
# Dispatcher Statistics
# ============================================================

dispatch_count = 0

strategy_dispatch_count = 0

candle_dispatch_count = 0

strategy_queue_full_count = 0

candle_queue_full_count = 0


# ============================================================
# Tick Dispatcher
# ============================================================

def dispatch_tick(tick):

    global dispatch_count
    global strategy_dispatch_count
    global candle_dispatch_count

    global strategy_queue_full_count
    global candle_queue_full_count

    dispatch_count += 1

    # ========================================================
    # Strategy Queue
    # ========================================================

    try:

        strategy_queue.put_nowait(
            tick
        )

        strategy_dispatch_count += 1

    except Full:

        strategy_queue_full_count += 1

        logger.error(
            f"Strategy queue FULL | "
            f"tick={dispatch_count} | "
            f"token={tick.token}"
        )

    # ========================================================
    # Candle Queue
    # ========================================================

    try:

        candle_queue.put_nowait(
            tick
        )

        candle_dispatch_count += 1

    except Full:

        candle_queue_full_count += 1

        logger.error(
            f"Candle queue FULL | "
            f"tick={dispatch_count} | "
            f"token={tick.token}"
        )

    # ========================================================
    # Debug
    # ========================================================

    if (
        dispatch_count % 100
        == 0
    ):

        logger.info(
            f"DISPATCH PROGRESS | "
            f"received={dispatch_count} | "
            f"strategy={strategy_dispatch_count} | "
            f"candle={candle_dispatch_count} | "
            f"strategy_full={strategy_queue_full_count} | "
            f"candle_full={candle_queue_full_count}"
        )


# ============================================================
# Main
# ============================================================

def main():

    logger.info(
        "========================================"
    )

    logger.info(
        "Paper Trading DATABASE REPLAY"
    )

    logger.info(
        "========================================"
    )

    # ========================================================
    # Strategy Thread
    # ========================================================

    strategy_thread = threading.Thread(
        target=strategy_worker.run,
        daemon=True,
        name="StrategyWorker",
    )

    # ========================================================
    # Candle Thread
    # ========================================================

    candle_thread = threading.Thread(
        target=candle_worker.run,
        daemon=True,
        name="CandleWorker",
    )

    # ========================================================
    # Start Workers
    # ========================================================

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
    # Tick Replay
    # ========================================================

    replay = TickReplay(

        db_path=(
            "database/"
            "papertrading.db"
        ),

        tick_handler=dispatch_tick,

        # --------------------------------
        # 1.0 = real historical timing
        # 10 = 10x faster
        # 0 = fastest
        # --------------------------------

        speed=1.0,

        log_every=100,
    )

    # ========================================================
    # Run Replay
    # ========================================================

    try:

        replay.run(
            token="483079",
        )

    except KeyboardInterrupt:

        logger.warning(
            "Replay stopped by user"
        )

    except Exception:

        logger.exception(
            "Replay failed"
        )

    finally:

        logger.info(
            "Stopping workers..."
        )

        stop_event.set()

        strategy_thread.join()

        candle_thread.join()

        # ====================================================
        # Final Statistics
        # ====================================================

        logger.info(
            "========================================"
        )

        logger.info(
            "FINAL DISPATCH STATISTICS"
        )

        logger.info(
            f"Received: "
            f"{dispatch_count}"
        )

        logger.info(
            f"Strategy dispatched: "
            f"{strategy_dispatch_count}"
        )

        logger.info(
            f"Candle dispatched: "
            f"{candle_dispatch_count}"
        )

        logger.info(
            f"Strategy queue full: "
            f"{strategy_queue_full_count}"
        )

        logger.info(
            f"Candle queue full: "
            f"{candle_queue_full_count}"
        )

        logger.info(
            f"Chart clients at shutdown: "
            f"{chart_broadcaster.client_count()}"
        )

        logger.info(
            "========================================"
        )

        logger.info(
            "Paper Trading Replay stopped"
        )


# ============================================================
# Entry Point
# ============================================================

if __name__ == "__main__":

    main()