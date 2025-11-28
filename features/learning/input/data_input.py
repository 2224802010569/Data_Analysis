import pandas as pd
from features.data.output.data_output import DataOutput

class DataInput:
    def __init__(self):
        self.data_output = DataOutput()

    def load(self, timeframe: str = "1M") -> pd.DataFrame:
        df = self.data_output.get(timeframe=timeframe)
        df = df.dropna(subset=["timestamp", "close"])
        return df
