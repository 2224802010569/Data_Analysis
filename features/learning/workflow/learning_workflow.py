from features.learning.usecase.fetch_and_save import FetchAndSaveUseCase
from features.learning.usecase.load import LoadUseCase

class LearninglWorkflow:
    def __init__(self):
        self.load = LoadUseCase().load

    def run(self):
        df = self.load()
        if not df:
            FetchAndSaveUseCase().execute()
            df = self.load()
        return df