

from datetime import datetime
from features.label.usecase.fetch_and_save import FetchAndSaveUseCase
from features.label.usecase.labels import LabelUsecase
from features.label.usecase.load import LoadUseCase


class LabelWorkflow:
    def __init__(self):
        self.load = LoadUseCase().load

    def run(self, timeframe: str = "1M"):
        df = self.load(timeframe=timeframe)
        if not df:
            FetchAndSaveUseCase().execute()
            df = self.load(timeframe=timeframe)
        return df