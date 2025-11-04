import pandas as pd
from datetime import timedelta
from app.config import config
from features.data.services.csv_service import CSVService


class CleanDataUseCase:
    """
    Clean and standardize raw Candle data for all configured timeframes.
    - Removes duplicates
    - Sorts by timestamp
    - Optionally fills missing Candles
    - Saves cleaned files to data/processed/
    """

    def __init__(self, store_port: CSVService = None):
        self.raw_store = store_port or CSVService()
        self.output_dir = self.raw_store.base_dir        
        if config.AUTO_CREATE_DIRS:
            self.output_dir.mkdir(parents=True, exist_ok=True)

    def execute(self, symbol: str = None, timeframes: list[str] = None, fill_missing: bool = True):
        symbol = symbol or config.SYMBOL
        timeframes = timeframes or config.TIMEFRAMES

        print(f"🧹 Cleaning data for {symbol}...")

        for tf in timeframes:
            filename = f"{symbol.replace('/', '_')}_{tf}.csv"
            raw_path = self.raw_store.base_dir / filename
            clean_path = self.output_dir / filename

            if not raw_path.exists():
                print(f"⚠️ Raw file not found: {raw_path}")
                continue

            df = pd.read_csv(raw_path, encoding=config.CSV_ENCODING)
            if df.empty:
                print(f"⚠️ Empty file: {filename}")
                continue

            # --- làm sạch ---
            df = df.drop_duplicates(subset=["timestamp"])
            df = df.dropna(subset=["timestamp", "open", "high", "low", "close", "volume"])
            df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
            df = df.sort_values("timestamp").reset_index(drop=True)

            # --- fill missing Candle nếu cần ---
            if fill_missing:
                df = self._fill_missing(df, tf)

            df.to_csv(clean_path, index=False, encoding=config.CSV_ENCODING)
            print(f"✅ Cleaned {len(df)} rows → {clean_path.name}")

        print(f"🏁 Cleaning complete for {symbol}.")

    # --- Helper ---
    def _fill_missing(self, df: pd.DataFrame, timeframe: str) -> pd.DataFrame:
        tf = timeframe.lower()
        if tf.endswith("h"):
            freq = f"{tf[:-1]}H"
        elif tf.endswith("d"):
            freq = f"{tf[:-1]}D"
        elif tf.endswith("M"):
            freq = f"{tf[:-1]}M"
        else:
            print(f"⚠️ Unsupported timeframe: {timeframe}")
            return df

        full_range = pd.date_range(df["timestamp"].min(), df["timestamp"].max(), freq=freq)
        df = df.drop_duplicates(subset=["timestamp"]).set_index("timestamp").reindex(full_range)
        df.index.name = "timestamp"

        # forward fill giá, volume=0 nếu thiếu
        df["open"] = df["open"].ffill()
        df["high"] = df["high"].ffill()
        df["low"] = df["low"].ffill()
        df["close"] = df["close"].ffill()
        df["volume"] = df["volume"].fillna(0)

        return df.reset_index()

