from dataclasses import dataclass
from datetime import datetime


@dataclass
class Candle:

    timestamp: datetime

    open: int
    high: int
    low: int
    close: int

    volume: int = 0