import pandas as pd
from app.config import config
from features.data.usecase.fetch_and_save_data import FetchAndSaveDataUseCase
from features.data.usecase.load import LoadUseCase

class DataWorkflow:
    def run(self, type: str = "sql", timeframe: str = "1M"):
        # ---  LUÔN TẢI DỮ LIỆU MỚI ---
        print(f"🚀 Bắt buộc cập nhật dữ liệu mới nhất cho {timeframe}...")
        FetchAndSaveDataUseCase().execute(timeframes=[timeframe])
        
        # Sau khi tải xong mới load lên
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

if __name__ == "__main__":
    # Chạy thử luôn với khung ngày (1d) để vẽ biểu đồ
    DataWorkflow().run(timeframe="1d")