
from datetime import datetime
from features.label.input.data_input import DataInput
from features.label.input.engineering_input import EngineeringInput
from features.label.service.label_service import LabelService
from features.label.service.sql_service import SQLService
from features.label.service.window_service import WindowService


class CreateLabel:
    def __init__(self):
        self.d_data = DataInput()
        self.e_data = EngineeringInput()
        self.sliding_window = WindowService().sliding_window
        self.label = LabelService()
        self.sql = SQLService()
    
    def execute(self, timerange:list[datetime, datetime], timeframe: str = "1M"):
        e,d = self._get_data(timerange, timeframe)
        df = self.sliding_window(e_data=e, d_data=d)
        df = self.label.generate_labels(df)
        self.sql.save(df)
        return df

    def _get_data(self, timerange:list[datetime, datetime], timeframe: str = "1M"):
        pass