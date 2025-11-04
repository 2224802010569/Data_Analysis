from typing import Protocol, List
from features.data.domain.entities.candle import Candle

class DataStorePort(Protocol):
    def save(self, symbol: str, data: List[Candle]) -> None:
        pass
