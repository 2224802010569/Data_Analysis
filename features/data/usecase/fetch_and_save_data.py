from app.config import config
from features.data.service.clean_service import CleanService
from features.data.service.sql_service import SQLService
from features.data.service.fetch_ccxt_service import CCXTService
from features.data.service.csv_service import CSVService

class FetchAndSaveDataUseCase:
    def __init__(self):
        self.fetch_port = CCXTService()
        self.csv_service = CSVService()
        self.sql_service = SQLService()

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
            print(f"  ▶ timeframe = {tf} ...")
            data = self.fetch_port.fetch(symbol=symbol, timeframe=tf, since=since, until=until)
            print(f"    → fetched {len(data)} Candles for {tf}")
            data = CleanService().execute(data)
            self.csv_service.save(symbol=symbol, data=data, timeframe=tf)
            self.sql_service.save(tf, data)
