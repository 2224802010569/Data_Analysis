import ccxt.async_support as ccxt
from datetime import datetime
from app.config import config
from features.data.domain.entities.candle import Candle

class CCXTService:
    async def fetch(
        self,
        symbol: str = None,
        timeframe: str = None,
        since: datetime = None,
        until: datetime = None,
    ):
        # dùng config làm fallback
        symbol = symbol or config.SYMBOL
        timeframe = timeframe or config.TIMEFRAMES[1]  # mặc định daily nếu không truyền
        since = since or config.START_DATE
        until = until or config.END_DATE

        exchange_cls = getattr(ccxt, config.EXCHANGE)
        exchange = exchange_cls({
            "enableRateLimit": True,
            "timeout": int(config.API_TIMEOUT * 1000),
        })

        since_ms = int(since.timestamp() * 1000)
        Candles = []

        while True:
            ohlcv = await exchange.fetch_ohlcv(symbol, timeframe, since_ms, limit=1000)
            if not ohlcv:
                break

            for c in ohlcv:
                ts = datetime.utcfromtimestamp(c[0] / 1000)
                if ts > until:
                    break
                Candles.append(Candle(ts, c[1], c[2], c[3], c[4], c[5]))

            # stop conditions
            if len(ohlcv) < 1000 or ts >= until:
                break

            # next batch: set since to last timestamp + 1ms to avoid duplicate
            since_ms = int(ohlcv[-1][0]) + 1

        await exchange.close()
        return Candles
