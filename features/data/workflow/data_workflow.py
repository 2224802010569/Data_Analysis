# features/data/workflow/data_workflow.py
import pandas as pd
from app.config import config
from features.data.usecase.fetch_and_save_data import FetchAndSaveDataUseCase
from features.data.usecase.load import LoadUseCase

class DataWorkflow:
    def run(self, type: str = "sql", timeframe: str = "1M"):
        """Tải dữ liệu từ SQLite hoặc CSV; nếu chưa có thì fetch mới."""
        data = LoadUseCase().load(type=type, timeframe=timeframe)
        if not data:
            print(f"fetching new data...")
            FetchAndSaveDataUseCase().execute(timeframes=[timeframe])
            data = LoadUseCase().load(type=type, timeframe=timeframe)

        # Chuyển list[Candle] → DataFrame
        if isinstance(data, list) and len(data) > 0:
            df = pd.DataFrame([{
                "timestamp": c.timestamp,
                "open": c.open,
                "high": c.high,
                "low": c.low,
                "close": c.close,
                "volume": c.volume,
                "timeframe": c.timeframe
            } for c in data])
        else:
            df = pd.DataFrame()
        return df
