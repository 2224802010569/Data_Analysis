import pandas as pd
from features.engineering.usecase.fetch_and_save import FetchAndSaveDataUseCase
from features.engineering.usecase.load import LoadUseCase
from app.config import config as con

class PureWorkflow:

    def __init__(self, entity):
        self.entity = entity

    def run(self, timeframe: str = "1M", df: pd.DataFrame = None) -> pd.DataFrame:
        loader = LoadUseCase(self.entity)
        data = loader.load(timeframe=timeframe)
        if not data:
            for tf in con.TIMEFRAMES:
                FetchAndSaveDataUseCase(self.entity).execute(df)
            data = loader.load(timeframe=timeframe)

        if not data:
            return pd.DataFrame()

        return pd.DataFrame([e.__dict__ for e in data])
