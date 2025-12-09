import pandas as pd
from features.label.output.label_output import LabelOutput

class LabelInput:

    def __init__(self):
        self.e_output = LabelOutput()

    def load(self, timeframe: str = "1M") -> pd.DataFrame:
        df = self.e_output.get(timeframe=timeframe)
        return df
