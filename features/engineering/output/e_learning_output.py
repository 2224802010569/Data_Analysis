from typing import Optional
import pandas as pd
from features.engineering.workflow.learing_workflow import LearningWorkflow

class ELearningOutput:
    def __init__(self):
        self.workflow = LearningWorkflow()

    def get(self, timeframe: str = "1M") -> pd.DataFrame:
        return self.workflow.run(timeframe=timeframe)
