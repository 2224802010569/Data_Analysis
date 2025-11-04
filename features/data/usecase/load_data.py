import pandas as pd
from pathlib import Path
from app.config import config
from features.data.services.csv_service import CSVService


class LoadDataUseCase:
    def __init__(self, store_port: CSVService = None):
        self.raw_store = store_port or CSVService()
        self.raw_dir = self.raw_store.base_dir        
        self.raw_dir.mkdir(parents=True, exist_ok=True)

    def execute(self, symbol: str = None, timeframe: str = None):
        """
        Load dataset theo timeframe (hoặc merged nếu không truyền gì).
        Args:
            symbol (str): Ví dụ 'BTC/USDT'
            timeframe (str): '1h', '1d', '1M', hoặc 'merged'
        Returns:
            pandas.DataFrame hoặc None
        """
        symbol = symbol or config.SYMBOL
        timeframe = timeframe or "merged"

        # --- chọn file tương ứng ---
        if timeframe.lower() == "merged" or timeframe == None:
            filename = f"{symbol.replace('/', '_')}.csv"
        else:
            filename = f"{symbol.replace('/', '_')}_{timeframe}.csv"

        path = self.raw_dir / filename

        if not path.exists():
            print(f"⚠️ File not found: {path}")
            return None

        # --- đọc dữ liệu ---
        df = pd.read_csv(path, encoding=config.CSV_ENCODING)
        if "timestamp" not in df.columns or df.empty:
            print(f"⚠️ Invalid or empty data in {path.name}")
            return None

        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df = df.dropna(subset=["timestamp"])
        df = df.sort_values("timestamp").reset_index(drop=True)

        print(f"📖 Loaded {len(df)} rows from {path.name}")
        return df
