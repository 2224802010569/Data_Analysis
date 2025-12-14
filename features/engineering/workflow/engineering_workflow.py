# features/data/workflow/data_workflow.py
import pandas as pd
from features.engineering.usecase.fetch_and_save import FetchAndSaveDataUseCase
from features.engineering.usecase.load import LoadUseCase
from features.engineering.domain.entities.engineering import Engineering
from features.engineering.workflow.pure_workflow import PureWorkflow
from features.engineering.input.data_input import DataInput
from app.config import config as con
class DataWorkflow:
    def __init__(self):
        self.e=Engineering
        self.data = DataInput()

    def run(self, timeframe: str = "1M") -> pd.DataFrame:
        loader = LoadUseCase(self.e)
        data = loader.load(timeframe=timeframe)
        if not data:
            for tf in con.TIMEFRAMES:
                df = self.data.load(tf)
                FetchAndSaveDataUseCase(self.e).execute(df)
            data = loader.load(timeframe=timeframe)

        if not data:
            return pd.DataFrame()
        return pd.DataFrame([e.__dict__ for e in data])
