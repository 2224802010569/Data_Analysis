# features/data/workflow/data_workflow.py
import pandas as pd
from features.data.domain.entities.candle import Candle
from features.engineering.input.learning_input import LearningInput
from features.engineering.usecase.fetch_and_save import FetchAndSaveDataUseCase
from features.engineering.usecase.load import LoadUseCase
from features.engineering.domain.entities.engineering_forecast import Engineering_Forecast
from features.engineering.workflow.pure_workflow import PureWorkflow
from app.config import config as con

class LearningWorkflow:
    def __init__(self):
        self.e=Engineering_Forecast
        self.data = LearningInput()

    def run(self, timeframe: str = "1M") -> pd.DataFrame:
        loader = LoadUseCase(self.e)
        data = loader.load(timeframe=timeframe)
        if not data:
            for tf in con.TIMEFRAMES:
                df = self.data.load(tf)
                candles = [
                    Candle(
                        timestamp=row["timestamp"],
                        open=float(row["open"]),
                        high=float(row["high"]),
                        low=float(row["low"]),
                        close=float(row["close"]),
                        volume=float(row["volume"]),
                        timeframe=tf,
                    )
                    for _, row in df.iterrows()
                ]
                df = pd.DataFrame([c.__dict__ for c in candles])
                FetchAndSaveDataUseCase(self.e).execute(timeframes= tf, df=df)
            data = loader.load(timeframe=timeframe)

        if not data:
            return pd.DataFrame()
        return pd.DataFrame([e.__dict__ for e in data])
