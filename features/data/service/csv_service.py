import csv
import datetime
from pathlib import Path
from typing import List, Optional
from app.config import config as con
from features.data.domain.entities.candle import Candle

class CSVService:
    def __init__(self, base_dir: Optional[Path] = None):
        if base_dir is None:
            self.base_dir = Path(__file__).resolve().parent.parent / "domain" / "storage"
        else:
            self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save(self, symbol: str = con.SYMBOL, data: list[Candle] = None, timeframe: Optional[str] = None) -> Path:
        if not data:
            print("⚠️ No data to save.")
            return

        timeframe_suffix = f"_{timeframe}" if timeframe else ""
        filename = f"{symbol.replace('/', '_')}{timeframe_suffix}.csv"
        path = self.base_dir / filename

        with path.open("w", newline="", encoding=con.CSV_ENCODING) as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "open", "high", "low", "close", "volume", "timeframe"])
            for c in data:
                writer.writerow([c.timestamp.isoformat(), c.open, c.high, c.low, c.close, c.volume, c.timeframe])

        print(f"✅ Saved {len(data)} Candles to {path}")
        return path

    def load(self, tf: str = "1M") -> List[Candle]:
        filename = f"{con.SYMBOL.replace('/', '_')}_{tf}.csv"
        path = self.base_dir / filename

        if not path.exists():
            print(f"⚠️ CSV file not found: {path}")
            return []

        candles: List[Candle] = []

        with path.open("r", newline="", encoding=con.CSV_ENCODING) as f:
            reader = csv.reader(f)
            try:
                next(reader)
            except StopIteration:
                return []

            for row in reader:
                ts_str, o_str, h_str, l_str, c_str, v_str, tf_str = row
                ts = datetime.fromtimestamp(ts_str / 1000) if isinstance(ts_str, (int, float)) else ts_str                
                candle = Candle(
                    timestamp=ts_str,
                    open=float(o_str),
                    high=float(h_str),
                    low=float(l_str),
                    close=float(c_str),
                    volume=float(v_str),
                    timeframe=tf_str
                )
                candles.append(candle)

        print(f"✅ Loaded {len(candles)} rows from CSV ({tf})")
        return candles


