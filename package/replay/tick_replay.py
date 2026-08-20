import sqlite3
import time

from package.tick import Tick
from package.logger import get_logger


class TickReplay:

    def __init__(
        self,
        db_path,
        tick_handler,
        speed=1.0,
        log_every=100,
    ):

        self.db_path = db_path
        self.tick_handler = tick_handler

        # 1.0 = original timing
        # 10.0 = 10x faster
        # 0   = maximum speed / no sleep
        self.speed = speed

        # Print progress after every N ticks
        self.log_every = log_every

        self.logger = get_logger(__name__)

        # Statistics
        self.total_ticks = 0
        self.dispatched_ticks = 0
        self.failed_ticks = 0

    def run(
        self,
        token=None,
        start_timestamp=None,
        end_timestamp=None,
    ):

        connection = sqlite3.connect(
            self.db_path
        )

        try:

            cursor = connection.cursor()

            # =================================================
            # Build Query
            # =================================================

            query = """
                SELECT *
                FROM ticks
                WHERE 1=1
            """

            parameters = []

            # -------------------------------------------------
            # Token
            # -------------------------------------------------

            if token is not None:

                query += """
                    AND token = ?
                """

                parameters.append(token)

            # -------------------------------------------------
            # Start timestamp
            # -------------------------------------------------

            if start_timestamp is not None:

                query += """
                    AND exchange_timestamp >= ?
                """

                parameters.append(
                    start_timestamp
                )

            # -------------------------------------------------
            # End timestamp
            # -------------------------------------------------

            if end_timestamp is not None:

                query += """
                    AND exchange_timestamp <= ?
                """

                parameters.append(
                    end_timestamp
                )

            # -------------------------------------------------
            # Correct chronological order
            # -------------------------------------------------

            query += """
                ORDER BY
                    exchange_timestamp ASC,
                    id ASC
            """

            # =================================================
            # Count matching rows FIRST
            # =================================================

            count_query = """
                SELECT COUNT(*)
                FROM ticks
                WHERE 1=1
            """

            count_parameters = []

            if token is not None:

                count_query += """
                    AND token = ?
                """

                count_parameters.append(
                    token
                )

            if start_timestamp is not None:

                count_query += """
                    AND exchange_timestamp >= ?
                """

                count_parameters.append(
                    start_timestamp
                )

            if end_timestamp is not None:

                count_query += """
                    AND exchange_timestamp <= ?
                """

                count_parameters.append(
                    end_timestamp
                )

            cursor.execute(
                count_query,
                count_parameters
            )

            total_database_ticks = (
                cursor.fetchone()[0]
            )

            # =================================================
            # Replay information
            # =================================================

            self.logger.info(
                "========================================"
            )

            self.logger.info(
                "TICK REPLAY START"
            )

            self.logger.info(
                f"Database: {self.db_path}"
            )

            self.logger.info(
                f"Token: {token}"
            )

            self.logger.info(
                f"Database ticks available: "
                f"{total_database_ticks}"
            )

            self.logger.info(
                f"Replay speed: {self.speed}"
            )

            self.logger.info(
                "========================================"
            )

            if total_database_ticks == 0:

                self.logger.warning(
                    "No tick data found in database"
                )

                return

            # =================================================
            # Load rows
            # =================================================

            cursor.execute(
                query,
                parameters
            )

            rows = cursor.fetchall()

            columns = [
                description[0]
                for description in cursor.description
            ]

            self.logger.info(
                f"Ticks loaded from database: "
                f"{len(rows)}"
            )

            # =================================================
            # Replay
            # =================================================

            previous_timestamp = None

            for row in rows:

                try:

                    data = dict(
                        zip(
                            columns,
                            row
                        )
                    )

                    current_timestamp = (
                        data["exchange_timestamp"]
                    )

                    # =========================================
                    # Preserve historical timing
                    # =========================================

                    if (
                        previous_timestamp is not None
                        and self.speed > 0
                    ):

                        difference_ms = (
                            current_timestamp
                            - previous_timestamp
                        )

                        delay = (
                            difference_ms / 1000
                        ) / self.speed

                        if delay > 0:

                            time.sleep(
                                delay
                            )

                    previous_timestamp = (
                        current_timestamp
                    )

                    # =========================================
                    # Build Tick
                    # =========================================

                    tick_data = {
                        "subscription_mode":
                            data["subscription_mode"],

                        "exchange_type":
                            data["exchange_type"],

                        "token":
                            data["token"],

                        "sequence_number":
                            data["sequence_number"],

                        "exchange_timestamp":
                            data["exchange_timestamp"],

                        "last_traded_price":
                            data["last_traded_price"],

                        "subscription_mode_val":
                            data["subscription_mode_val"],

                        "last_traded_quantity":
                            data["last_traded_quantity"],

                        "average_traded_price":
                            data["average_traded_price"],

                        "volume_trade_for_the_day":
                            data["volume_trade_for_the_day"],

                        "total_buy_quantity":
                            data["total_buy_quantity"],

                        "total_sell_quantity":
                            data["total_sell_quantity"],

                        "open_price_of_the_day":
                            data["open_price_of_the_day"],

                        "high_price_of_the_day":
                            data["high_price_of_the_day"],

                        "low_price_of_the_day":
                            data["low_price_of_the_day"],

                        "closed_price":
                            data["closed_price"],

                        "last_traded_timestamp":
                            data["last_traded_timestamp"],

                        "open_interest":
                            data["open_interest"],

                        "open_interest_change_percentage":
                            data[
                                "open_interest_change_percentage"
                            ],

                        "upper_circuit_limit":
                            data["upper_circuit_limit"],

                        "lower_circuit_limit":
                            data["lower_circuit_limit"],

                        "52_week_high_price":
                            data["week_52_high_price"],

                        "52_week_low_price":
                            data["week_52_low_price"],

                        "best_5_buy_data":
                            data["best_5_buy_data"],

                        "best_5_sell_data":
                            data["best_5_sell_data"],

                        "depth_20_buy_data":
                            data["depth_20_buy_data"],

                        "depth_20_sell_data":
                            data["depth_20_sell_data"],

                        "packet_received_time":
                            data["packet_received_time"],
                    }

                    tick = Tick(
                        tick_data
                    )

                    # =========================================
                    # Send tick into pipeline
                    # =========================================

                    self.tick_handler(
                        tick
                    )

                    self.total_ticks += 1
                    self.dispatched_ticks += 1

                    # =========================================
                    # Debug every N ticks
                    # =========================================

                    if (
                        self.total_ticks
                        % self.log_every
                        == 0
                    ):

                        self.logger.info(
                            f"REPLAY PROGRESS | "
                            f"database={total_database_ticks} | "
                            f"read={self.total_ticks} | "
                            f"dispatched={self.dispatched_ticks} | "
                            f"failed={self.failed_ticks}"
                        )

                        self.logger.debug(
                            f"LAST TICK | "
                            f"token={tick.token} | "
                            f"timestamp={tick.exchange_timestamp} | "
                            f"price={tick.last_traded_price}"
                        )

                except Exception:

                    self.failed_ticks += 1

                    self.logger.exception(
                        f"Failed to replay tick | "
                        f"read={self.total_ticks + 1}"
                    )

            # =================================================
            # Final statistics
            # =================================================

            self.logger.info(
                "========================================"
            )

            self.logger.info(
                "TICK REPLAY COMPLETED"
            )

            self.logger.info(
                f"Database ticks available: "
                f"{total_database_ticks}"
            )

            self.logger.info(
                f"Ticks read: "
                f"{self.total_ticks}"
            )

            self.logger.info(
                f"Ticks dispatched: "
                f"{self.dispatched_ticks}"
            )

            self.logger.info(
                f"Failed ticks: "
                f"{self.failed_ticks}"
            )

            self.logger.info(
                "========================================"
            )

        finally:

            connection.close()