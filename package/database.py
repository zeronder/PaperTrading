import json
import sqlite3
from pathlib import Path


class Database:

    def __init__(self, db_path="database/papertrading.db"):
        self.db_path = Path(db_path)

        # database directory create karo
        self.db_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        self.connection = sqlite3.connect(
            self.db_path
        )

        self.create_tables()

    def create_tables(self):

        cursor = self.connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ticks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                subscription_mode INTEGER NOT NULL,
                exchange_type INTEGER NOT NULL,
                token TEXT NOT NULL,

                sequence_number INTEGER,
                exchange_timestamp INTEGER,

                last_traded_price INTEGER,

                subscription_mode_val TEXT,

                last_traded_quantity INTEGER,
                average_traded_price INTEGER,
                volume_trade_for_the_day INTEGER,

                total_buy_quantity REAL,
                total_sell_quantity REAL,

                open_price_of_the_day INTEGER,
                high_price_of_the_day INTEGER,
                low_price_of_the_day INTEGER,
                closed_price INTEGER,

                last_traded_timestamp INTEGER,

                open_interest INTEGER,
                open_interest_change_percentage INTEGER,

                upper_circuit_limit INTEGER,
                lower_circuit_limit INTEGER,

                week_52_high_price INTEGER,
                week_52_low_price INTEGER,

                packet_received_time INTEGER,

                best_5_buy_data TEXT,
                best_5_sell_data TEXT,

                depth_20_buy_data TEXT,
                depth_20_sell_data TEXT,

                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.connection.commit()

        self.migrate_ticks()


    def migrate_ticks(self):

        cursor = self.connection.cursor()

        cursor.execute("PRAGMA table_info(ticks)")

        columns = {
            row[1]
            for row in cursor.fetchall()
        }

        new_columns = {
            "best_5_buy_data": "TEXT",
            "best_5_sell_data": "TEXT",
            "depth_20_buy_data": "TEXT",
            "depth_20_sell_data": "TEXT",
        }

        for column, column_type in new_columns.items():

            if column not in columns:

                cursor.execute(
                    f"""
                    ALTER TABLE ticks
                    ADD COLUMN {column} {column_type}
                    """
                )

        self.connection.commit()

    def insert_ticks(self, ticks):

        cursor = self.connection.cursor()

        try:
            for tick in ticks:

                cursor.execute("""
                    INSERT INTO ticks (
                        subscription_mode,
                        exchange_type,
                        token,
                        sequence_number,
                        exchange_timestamp,
                        last_traded_price,
                        subscription_mode_val,
                        last_traded_quantity,
                        average_traded_price,
                        volume_trade_for_the_day,
                        total_buy_quantity,
                        total_sell_quantity,
                        open_price_of_the_day,
                        high_price_of_the_day,
                        low_price_of_the_day,
                        closed_price,
                        last_traded_timestamp,
                        open_interest,
                        open_interest_change_percentage,
                        upper_circuit_limit,
                        lower_circuit_limit,
                        week_52_high_price,
                        week_52_low_price,
                        packet_received_time,
                        best_5_buy_data,
                        best_5_sell_data,
                        depth_20_buy_data,
                        depth_20_sell_data
                    )
                    VALUES (
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                        ?, ?, ?, ?, ?, ?, ?, ?
                    )
                """, (
                    tick.subscription_mode,
                    tick.exchange_type,
                    tick.token,
                    tick.sequence_number,
                    tick.exchange_timestamp,
                    tick.last_traded_price,
                    tick.subscription_mode_val,
                    tick.last_traded_quantity,
                    tick.average_traded_price,
                    tick.volume_trade_for_the_day,
                    tick.total_buy_quantity,
                    tick.total_sell_quantity,
                    tick.open_price_of_the_day,
                    tick.high_price_of_the_day,
                    tick.low_price_of_the_day,
                    tick.closed_price,
                    tick.last_traded_timestamp,
                    tick.open_interest,
                    tick.open_interest_change_percentage,
                    tick.upper_circuit_limit,
                    tick.lower_circuit_limit,
                    tick.week_52_high_price,
                    tick.week_52_low_price,
                    tick.packet_received_time,
                    json.dumps(tick.best_5_buy_data),
                    json.dumps(tick.best_5_sell_data),
                    json.dumps(tick.depth_20_buy_data),
                    json.dumps(tick.depth_20_sell_data),
                ))

            self.connection.commit()

        except Exception:
            self.connection.rollback()
            raise

    def close(self):
        self.connection.close()