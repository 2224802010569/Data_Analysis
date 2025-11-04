from typing import Protocol, List
from datetime import datetime
from features.data.domain.entities.candle import Candle

class DataFetchPort(Protocol):
    async def fetch(
        self,
        symbol: str,
        timeframe: str,
        since: datetime,
        until: datetime,
    ) -> List[Candle]:
        pass
