import pandas as pd
from features.learning.workflow.learning_workflow import LearninglWorkflow

class LearningOutput:
    def __init__(self):
        self.workflow = LearninglWorkflow()

    def get(self):
        df = self.workflow.run()
        return df