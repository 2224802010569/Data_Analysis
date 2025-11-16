from typing import Optional
import pandas as pd
from features.data.output.data_output import DataOutput

class DataInput:
    """
    Adapter lấy dữ liệu từ feature `data` và chuẩn hóa nhẹ cho `feature_engineering`.
    Input: DataFrame (timestamp, open, high, low, close, volume, timeframe)
    Output: DataFrame đã làm sạch và sẵn sàng tính chỉ báo.
    """
    _cache:Optional[pd.DataFrame] = None

    def __init__(self):
        self.data_output = DataOutput()

    def load(self, timeframe: str = "1M") -> pd.DataFrame:
        if DataInput._cache is not None:
            return DataInput._cache
        DataInput._cache = self.data_output.get(timeframe=timeframe)
        if not pd.api.types.is_datetime64_any_dtype(DataInput._cache["timestamp"]):
            DataInput._cache["timestamp"] = pd.to_datetime(DataInput._cache["timestamp"], errors="coerce")
        DataInput._cache = DataInput._cache.dropna(subset=["timestamp", "close"])

        print(f"✅ FeatureInputAdapter loaded {len(DataInput._cache)} rows for timeframe {timeframe}")
        return DataInput._cache
