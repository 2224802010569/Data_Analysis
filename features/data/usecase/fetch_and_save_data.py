from app.config import config
from features.data.services.fetch_ccxt_service import CCXTService
from features.data.services.csv_service import CSVService

class FetchAndSaveDataUseCase:
    def __init__(self):
        self.fetch_port = CCXTService()
        self.store_port = CSVService()

    async def execute(
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

        print(f"🔄 Fetching data for {symbol} from {since.date()} to {until.date()}...")
        total = 0
        for tf in timeframes:
            print(f"  ▶ timeframe = {tf} ...")
            data = await self.fetch_port.fetch(symbol=symbol, timeframe=tf, since=since, until=until)
            print(f"    → fetched {len(data)} Candles for {tf}")
            self.store_port.save(symbol=symbol, data=data, timeframe=tf)
            total += len(data)
        print(f"✅ Fetch and save complete. Total Candles fetched across timeframes: {total}")
