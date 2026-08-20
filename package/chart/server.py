import json
import time

from flask import (
    Flask,
    Response,
    jsonify,
    render_template,
)

from package.logger import get_logger


def create_chart_server(
    candle_store,
    chart_broadcaster,
):

    app = Flask(
        __name__,
        template_folder="templates",
    )

    logger = get_logger(
        __name__
    )

    # ========================================================
    # Chart Page
    # ========================================================

    @app.get("/")
    def chart():

        return render_template(
            "chart.html"
        )

    # ========================================================
    # Historical Candles
    # ========================================================

    @app.get("/api/candles")
    def get_candles():

        candles = (
            candle_store.get_all()
        )

        current = (
            candle_store.get_current()
        )

        data = []

        # ----------------------------------------------------
        # Completed candles
        # ----------------------------------------------------

        for candle in candles:

            data.append({

                "time": int(
                    candle.timestamp.timestamp()
                ),

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
            })

        # ----------------------------------------------------
        # Current running candle
        # ----------------------------------------------------

        if current is not None:

            data.append({

                "time": int(
                    current.timestamp.timestamp()
                ),

                "open": float(
                    current.open
                ),

                "high": float(
                    current.high
                ),

                "low": float(
                    current.low
                ),

                "close": float(
                    current.close
                ),

                "volume": int(
                    current.volume
                ),
            })

        logger.info(
            "Historical candles requested | "
            f"closed={len(candles)} | "
            f"current={current is not None}"
        )

        return jsonify(data)

    # ========================================================
    # Live Candle Stream
    # ========================================================

    @app.get("/api/candle-stream")
    def candle_stream():

        client_queue = (
            chart_broadcaster.subscribe()
        )

        logger.info(
            "Chart SSE client connected | "
            f"clients="
            f"{chart_broadcaster.client_count()}"
        )

        def generate():

            try:

                # ============================================
                # SSE connection
                # ============================================

                yield (
                    "event: connected\n"
                    "data: "
                    "{\"status\":\"connected\"}\n\n"
                )

                # ============================================
                # Keep connection alive
                # ============================================

                while True:

                    try:

                        message = (
                            client_queue.get(
                                timeout=15
                            )
                        )

                        # ------------------------------------
                        # Send message immediately
                        # ------------------------------------

                        yield message

                    except Exception:

                        # ------------------------------------
                        # SSE heartbeat
                        # ------------------------------------

                        yield (
                            ": heartbeat\n\n"
                        )

            except GeneratorExit:

                logger.info(
                    "Chart SSE generator closed"
                )

            except Exception:

                logger.exception(
                    "Chart SSE generator failed"
                )

            finally:

                chart_broadcaster.unsubscribe(
                    client_queue
                )

                logger.info(
                    "Chart SSE client disconnected | "
                    f"clients="
                    f"{chart_broadcaster.client_count()}"
                )

        response = Response(
            generate(),
            mimetype="text/event-stream",
        )

        # ====================================================
        # Important SSE headers
        # ====================================================

        response.headers[
            "Cache-Control"
        ] = (
            "no-cache, no-store, "
            "must-revalidate"
        )

        response.headers[
            "Pragma"
        ] = "no-cache"

        response.headers[
            "Expires"
        ] = "0"

        response.headers[
            "X-Accel-Buffering"
        ] = "no"

        response.headers[
            "Connection"
        ] = "keep-alive"

        return response

    return app