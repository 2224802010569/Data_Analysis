# features/data/workflow/data_workflow.py
import pandas as pd
from features.engineering.usecase.fetch_and_save import FetchAndSaveDataUseCase
from features.engineering.usecase.load import LoadUseCase

class DataWorkflow:
    def run(self,timeframe: str = "1M"):
        data = LoadUseCase().load(timeframe=timeframe)
        if not data:
            print(f"fetching new data...")
            FetchAndSaveDataUseCase().execute(timeframes=[timeframe])
            data = LoadUseCase().load(timeframe=timeframe)

        if isinstance(data, list) and len(data) > 0:
            df = pd.DataFrame([{
                "timestamp": e.timestamp,
                "timeframe" : e.timeframe,
                "indicator": e.indicator,
                "temporal": e.temporal
            } for e in data])
        else:
            df = pd.DataFrame()
        return df
