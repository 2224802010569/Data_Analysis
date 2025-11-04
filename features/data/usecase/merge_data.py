import pandas as pd
from pathlib import Path
from app.config import config
from features.data.services.csv_service import CSVService


class MergeDataUseCase:
    """
    Hợp nhất dữ liệu đã clean từ nhiều timeframe (1h, 1d, 1M)
    thành một file duy nhất, lưu tại data/domain/raw.
    """

    def __init__(self, store_port: CSVService = None):
        self.raw_store = store_port or CSVService()
        self.output_dir = self.raw_store.base_dir        
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def execute(self, symbol: str = None, timeframes: list[str] = None):
        symbol = symbol or config.SYMBOL
        timeframes = timeframes or config.TIMEFRAMES

        print(f"🔗 Merging cleaned data for {symbol} across {timeframes}...")

        merged_df = None

        for tf in timeframes:
            filename = f"{symbol.replace('/', '_')}_{tf}.csv"
            file_path = self.output_dir / filename

            if not file_path.exists():
                print(f"⚠️ File not found: {file_path}")
                continue

            df = pd.read_csv(file_path, encoding=config.CSV_ENCODING)
            if "timestamp" not in df.columns or df.empty:
                print(f"⚠️ Invalid or empty data for {tf}, skipping.")
                continue

            # Đảm bảo timestamp là datetime
            df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
            df = df.dropna(subset=["timestamp"])

            # Đổi tên cột theo timeframe
            rename_map = {
                "open": f"open_{tf}",
                "high": f"high_{tf}",
                "low": f"low_{tf}",
                "close": f"close_{tf}",
                "volume": f"volume_{tf}",
            }
            df = df.rename(columns=rename_map)

            # Merge theo timestamp
            if merged_df is None:
                merged_df = df
            else:
                merged_df = pd.merge(merged_df, df, on="timestamp", how="outer")

        if merged_df is None or merged_df.empty:
            print("❌ No valid data found to merge.")
            return None

        merged_df = merged_df.sort_values("timestamp").reset_index(drop=True)

        # Lưu kết quả
        output_file = self.output_dir / f"{symbol.replace('/', '_')}.csv"
        merged_df.to_csv(output_file, index=False, encoding=config.CSV_ENCODING)

        print(f"✅ Merged file saved: {output_file}")
        print(f"📊 Rows: {len(merged_df)}, Columns: {len(merged_df.columns)}")

        return merged_df
