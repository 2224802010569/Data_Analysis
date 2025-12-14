import pandas as pd
from features.learning.workflow.learning_workflow import LearningWorkflow

class LearningOutput:
    def __init__(self):
        self.workflow = LearningWorkflow()

    def get(self, timeframe:str = "1M") -> pd.DataFrame:
        df = self.workflow.run(timeframe)
        df = self._to_candles(df = df, timeframe= timeframe)
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