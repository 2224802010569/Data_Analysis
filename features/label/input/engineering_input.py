import pandas as pd
from features.engineering.output.engineering_output import EngineeringOutput

class EngineeringInput:

    def __init__(self):
        self.e_output = EngineeringOutput()

    def load(self, timeframe: str = "1M") -> pd.DataFrame:
        df = self.e_output.get(timeframe=timeframe)
        df = df.dropna(subset=["timestamp", "close"])
        return df
