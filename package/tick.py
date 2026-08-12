class Tick:

    def __init__(self, data):

        self.subscription_mode = data["subscription_mode"]
        self.exchange_type = data["exchange_type"]
        self.token = data["token"]

        self.sequence_number = data.get("sequence_number")
        self.exchange_timestamp = data.get(
            "exchange_timestamp"
        )

        self.last_traded_price = data.get(
            "last_traded_price"
        )

        self.subscription_mode_val = data.get(
            "subscription_mode_val"
        )

        self.last_traded_quantity = data.get(
            "last_traded_quantity"
        )

        self.average_traded_price = data.get(
            "average_traded_price"
        )

        self.volume_trade_for_the_day = data.get(
            "volume_trade_for_the_day"
        )

        self.total_buy_quantity = data.get(
            "total_buy_quantity"
        )

        self.total_sell_quantity = data.get(
            "total_sell_quantity"
        )

        self.open_price_of_the_day = data.get(
            "open_price_of_the_day"
        )

        self.high_price_of_the_day = data.get(
            "high_price_of_the_day"
        )

        self.low_price_of_the_day = data.get(
            "low_price_of_the_day"
        )

        self.closed_price = data.get(
            "closed_price"
        )

        self.last_traded_timestamp = data.get(
            "last_traded_timestamp"
        )

        self.open_interest = data.get(
            "open_interest"
        )

        self.open_interest_change_percentage = data.get(
            "open_interest_change_percentage"
        )

        self.upper_circuit_limit = data.get(
            "upper_circuit_limit"
        )

        self.lower_circuit_limit = data.get(
            "lower_circuit_limit"
        )

        self.week_52_high_price = data.get(
            "52_week_high_price"
        )

        self.week_52_low_price = data.get(
            "52_week_low_price"
        )

        self.best_5_buy_data = data.get(
            "best_5_buy_data"
        )

        self.best_5_sell_data = data.get(
            "best_5_sell_data"
        )

        self.depth_20_buy_data = data.get(
            "depth_20_buy_data"
        )

        self.depth_20_sell_data = data.get(
            "depth_20_sell_data"
        )

        self.packet_received_time = data.get(
            "packet_received_time"
        )

        