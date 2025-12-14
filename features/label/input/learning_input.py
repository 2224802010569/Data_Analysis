from typing import Optional
import pandas as pd
from features.data.domain.entities.candle import Candle
from features.learning.output.learning_output import LearningOutput

class LearningInput:

    def __init__(self):
        self.data_output = LearningOutput()

    def load(self, timeframe: str = "1M") -> pd.DataFrame:
        df= self.data_output.get(timeframe=timeframe)
        if not pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
            df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df= df.dropna(subset=["timestamp", "close"])
        # df = self._to_candles(df = df, timeframe= timeframe)
        return df

    def _to_candles(self, df: pd.DataFrame, timeframe: str) -> pd.DataFrame:
        df = df.copy()
        df["timeframe"] = timeframe
        return pd.DataFrame({
            "timestamp": df["timestamp"],
            "open": df["open"].astype(float),
            "high": df["high"].astype(float),
            "low": df["low"].astype(float),
            "close": df["close"].astype(float),
            "volume": df["volume"].astype(float),
            "timeframe": df["timeframe"],
        })

