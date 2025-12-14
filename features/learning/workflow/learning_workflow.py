from features.learning.usecase.train import TrainUseCase
from features.learning.usecase.forecast import ForecastUseCase
from features.learning.usecase.load import LoadUseCase
from features.learning.service.history_service import HistoryService
from app.config import config as con

class LearningWorkflow:
    def __init__(self):
        self.train_uc = TrainUseCase()
        self.forecast_uc = ForecastUseCase()
        self.load_uc = LoadUseCase()
        self.history_service = HistoryService()

    def run(self, timeframe: str = "1M"):
        df = self.load_uc.load(timeframe=timeframe)
        if df is None or df.empty:
            for _ in range(con.NUMBER_MODULE_EACH_RUN):
                df=self.train_uc.execute()
                module_id = df["module_id"]
                for tf in con.TIMEFRAMES:
                    self.forecast_uc.execute(
                        module_id=module_id,
                        timeframe=tf,
                    )
            df = self.load_uc.load(timeframe=timeframe)
        return df
