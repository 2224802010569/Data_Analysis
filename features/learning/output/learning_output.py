import pandas as pd
from features.learning.workflow.learning_workflow import LearninglWorkflow

class DataOutput:
    def __init__(self):
        self.workflow = LearninglWorkflow()

    def get(self, type: str = "sql", timeframe: str = "1M") -> pd.DataFrame:
        df = self.workflow.run(type=type, timeframe=timeframe)
        return df