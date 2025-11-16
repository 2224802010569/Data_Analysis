from app.config import config
from features.engineering.service.sql_service import SQLService
from features.engineering.usecase.combine import CombineUseCase

class FetchAndSaveDataUseCase:
    def __init__(self):
        self.sql = SQLService()

    def execute(
        self,
        symbol: str = None,
        timeframes: list = None,
        since = None,
        until = None,
    ):
        symbol = symbol or config.SYMBOL
        timeframes = timeframes or config.TIMEFRAMES
        since = since or config.START_DATE
        until = until or config.END_DATE
        for tf in timeframes:
            print(f"▶ timeframe = {tf}")
            data = CombineUseCase().execute(tf)
            print(f"→ fetched {len(data)} engineering rows")
            self.sql.save(data)
