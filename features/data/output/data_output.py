# features/data/output/data_output.py
import pandas as pd
from features.data.workflow.data_workflow import DataWorkflow

class DataOutput:
    def __init__(self):
        self.workflow = DataWorkflow()

    def get(self, type: str = "sql", timeframe: str = "1M") -> pd.DataFrame:
        df = self.workflow.run(type=type, timeframe=timeframe)
        return df