import pandas as pd
from features.label.workflow.label_workflow import LabelWorkflow

class LabelOutput:
    def __init__(self):
        self.workflow = LabelWorkflow()

    def get(self, timeframe: str = "1M") -> pd.DataFrame:
        df = self.workflow.run(timeframe=timeframe)
        df = pd.DataFrame([vars(label) for label in df])
        return df