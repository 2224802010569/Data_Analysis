from features.learning.service.csv_service import CSVService
from features.learning.service.history_service import HistoryService
from app.config import config as con

class LoadUseCase:
    def __init__(self):
        self.history_service = HistoryService()
        self.csv_service = CSVService()

    def load(self, timeframe: str = "1M"):
        module_id = self.history_service._get_best_module_id(timeframe)
        if module_id is None:
            return None
        path = (
            con.LEARNING_DIR
            / module_id
            / f"forecast_{timeframe}.csv"
        )
        df = self.csv_service.read_dataframe(path)
        return df
