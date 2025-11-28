import pandas as pd
from features.label.workflow.label_workflow import LabelWorkflow

class EngineeringOutput:
    def __init__(self):
        self.workflow = LabelWorkflow()

    def get(self, timeframe: str = "1M") -> pd.DataFrame:
        df = self.workflow.run(timeframe=timeframe)
        if df.empty or df is None:
            print("⚠️ No data found for output.")
            return pd.DataFrame()
        return df