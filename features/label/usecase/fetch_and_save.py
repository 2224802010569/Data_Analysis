from app.config import config
from features.label.input.data_input import DataInput
from features.label.input.engineering_input import EngineeringInput
from features.label.service.sql_service import SQLService
from features.label.service.window_service import WindowService
class FetchAndSaveDataUseCase:
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
            data= WindowService().sliding_window(self, self.e_data.load(tf) , self.d_data.load(tf))
            self.sql.save(data)
