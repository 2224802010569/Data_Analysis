from app.config import config as con
from features.learning.service.data_service import DataService
from features.learning.service.forecast_service import ForecastService
from features.learning.service.model_service import ModelService
from features.learning.service.csv_service import CSVService
from features.learning.service.storage_service import StorageService


class ForecastUseCase:
    def __init__(self):
        self.data_service = DataService()
        self.model_service = ModelService()
        self.forecast_service = ForecastService()
        self.csv_service = CSVService()
        self.storage_service = StorageService()

    def execute(self, module_id: str, timeframe: str) -> dict:
        model, module = self.storage_service.load(module_id)
        df_candle, df_engineering = self.data_service.load_data(
            timeframe=timeframe
        )
        forecasts = self.forecast_service.forecast(
            model=model,
            df_candle=df_candle,
            df_engineering=df_engineering,
            module=module,
            timeframe=timeframe,
        )
        path = (
            con.LEARNING_DIR
            / module.module_id
            / f"forecast_{timeframe}.csv"
        )
        self.csv_service.write_forecast(
            forecasts=forecasts,
            path=path,
        )
        return {
            "module_id": module.module_id,
            "timeframe": timeframe,
            "forecast_path": str(path),
        }
