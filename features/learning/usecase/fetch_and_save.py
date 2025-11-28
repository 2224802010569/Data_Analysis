from app.config import config
from features.label.input.data_input import DataInput
from features.label.input.engineering_input import EngineeringInput
from features.label.service.sql_service import SQLService
from features.label.usecase.labels import LabelUsecase
class FetchAndSaveUseCase:
    def __init__(self):
        self.sql = SQLService()
        self.d_data = DataInput()
        self.e_data = EngineeringInput()

    def execute(
        self,
        symbol: str = None,
        timeframes: list = None,
        since = None,
        until = None,
    ):
        symbol = symbol or config.SYMBOL
        timeframes = timeframes or config.TIMEFRAMES
        since = since or config.START_DATE
        until = until or config.END_DATE

        for tf in timeframes:
            print(f"  ▶ timeframe = {tf} ...")
            data = LabelUsecase().execute(tf=tf)
            self.sql.save(data)
