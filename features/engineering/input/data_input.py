from typing import Optional
import pandas as pd
from features.data.output.data_output import DataOutput

class DataInput:

    def __init__(self):
        self.data_output = DataOutput()

    def load(self, timeframe: str = "1M") -> pd.DataFrame:
        df= self.data_output.get(timeframe=timeframe)
        if not pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
            df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df= df.dropna(subset=["timestamp", "close"])
        print(f"✅ FeatureInputAdapter loaded {len(df)} rows for timeframe {timeframe}")
        return df
