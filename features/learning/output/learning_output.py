import pandas as pd
from features.learning.workflow.learning_workflow import LearningWorkflow

class EngineeringOutput:
    def __init__(self):
        self.workflow = LearningWorkflow()

    def get(self) -> pd.DataFrame:
        df = self.workflow.run()
        return df