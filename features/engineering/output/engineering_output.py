from typing import Optional
import pandas as pd
from features.engineering.workflow.engineering_workflow import DataWorkflow

class EngineeringOutput:
    def __init__(self):
        self.workflow = DataWorkflow()

    def get(self, timeframe: str = "1M") -> pd.DataFrame:
        return self.workflow.run(timeframe=timeframe)
