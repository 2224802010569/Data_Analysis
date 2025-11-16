from typing import Optional
import pandas as pd
from features.engineering.workflow.engineering_workflow import DataWorkflow

class EngineeringOutput:
    _cache:Optional[pd.DataFrame] = None
    def __init__(self):
        self.workflow = DataWorkflow()

    def get(self, timeframe: str = "1M") -> pd.DataFrame:
        if EngineeringOutput._cache is not None:
            return EngineeringOutput._output
        EngineeringOutput._cache = self.workflow.run(timeframe=timeframe)
        return EngineeringOutput._cache