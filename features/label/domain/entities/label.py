from dataclasses import dataclass
from datetime import datetime

@dataclass
class Label:
    label: str
    timeframe: str
    t0: datetime
    t1: datetime
