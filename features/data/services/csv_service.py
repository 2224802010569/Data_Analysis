import csv
from pathlib import Path
from typing import Optional
from app.config import config
from features.data.domain.entities.candle import Candle

class CSVService:
    def __init__(self, base_dir: Optional[Path] = None):
        if base_dir is None:
            self.base_dir = Path(__file__).resolve().parent.parent / "domain" / "raw"
        else:
            self.base_dir = Path(base_dir)

        if config.AUTO_CREATE_DIRS:
            self.base_dir.mkdir(parents=True, exist_ok=True)

    def save(self, symbol: str, data: list[Candle], timeframe: Optional[str] = None) -> Path:
        if not data:
            print("⚠️ No data to save.")
            return

        timeframe_suffix = f"_{timeframe}" if timeframe else ""
        filename = f"{symbol.replace('/', '_')}{timeframe_suffix}.csv"
        path = self.base_dir / filename

        with path.open("w", newline="", encoding=config.CSV_ENCODING) as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "open", "high", "low", "close", "volume"])
            for c in data:
                writer.writerow([c.timestamp.isoformat(), c.open, c.high, c.low, c.close, c.volume])

        print(f"✅ Saved {len(data)} Candles to {path}")
        return path
