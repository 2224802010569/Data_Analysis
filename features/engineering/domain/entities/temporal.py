from dataclasses import dataclass
from datetime import datetime

@dataclass
class TemporalValues:
    time_sin: float
    time_cos: float
    return_1: float
    time_volatility: float

@dataclass
class Temporal:
    timestamp: datetime
    timeframe: str
    values: TemporalValues

    def get(self, key: str) -> float:
        return getattr(self.values, key)
