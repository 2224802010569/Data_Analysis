import pandas as pd
from features.engineering.output.e_learning_output import ELearningOutput

class EngineeringInput:

    def __init__(self):
        self.e_output = ELearningOutput()

    def load(self, timeframe: str = "1M") -> pd.DataFrame:
        df = self.e_output.get(timeframe=timeframe)
        df = df.dropna(subset=["timestamp", "close"])
        return df
