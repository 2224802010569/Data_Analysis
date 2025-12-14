import pandas as pd
from app.config import config
from features.engineering.service.sql_service import SQLService
from features.engineering.usecase.combine import CombineUseCase
class FetchAndSaveDataUseCase:
    def __init__(self, e):
        self.sql = SQLService(entities =e)

    def execute(
        self,
        timeframes: str = "1M",
        df: pd.DataFrame = None
    ):
        print("fecth\n", df.head())
        timeframes = timeframes
        data = CombineUseCase().execute(timeframe = timeframes, df=df)
        print(f"→ fetched {len(data)} engineering rows")
        self.sql.save(data)
