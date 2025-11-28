

from datetime import datetime
from features.data.usecase.fetch_and_save_data import FetchAndSaveDataUseCase
from features.label.usecase import create_label
from features.label.usecase.load import LoadUseCase


class LabelWorkflow:
    def __init__(self):
        self.load = LoadUseCase().load

    def run(self, timerange:list[datetime, datetime], timeframe: str = "1M"):
        df = self.load(timerange=timerange, timeframe=timeframe)
        if not df:
            # nếu chưa có bảng trong CSDL thì fetch và save dữ liệu
            FetchAndSaveDataUseCase().execute()
            df = self.load(timerange=timerange, timeframe=timeframe)
            if not df:
                df = create_label().execute(timerange=timerange, timeframe=timeframe)
        return df