from app.config import config as con
from features.learning.domain.entities.module import Module
from features.learning.service.history_service import HistoryService
from features.learning.service.meta_service import MetaService
from features.learning.service.train_service import TrainService
from features.learning.service.metric_service import MetricService
from features.learning.service.storage_service import StorageService

class TrainUseCase:
    def __init__(self):
        self.train_service = TrainService()
        self.metric_service = MetricService()
        self.history_usecase = HistoryService()
        self.meta_service = MetaService()
        self.storage_service = StorageService()

    def _resolve_module_config(self, module_config: dict = None) -> dict:
        if module_config:
            return module_config
        cfg = self.meta_service.suggest_from_history()
        if cfg:
            return cfg
        return self.meta_service.default_module_config()

    def execute(self, module_config: dict = None) -> dict:
        module_config = self._resolve_module_config(module_config)
        module = Module(**module_config)
        metrics_by_timeframe = {}
        for timeframe in con.TIMEFRAMES:
            model, df_candle, df_engineering = self.train_service.train(
                module=module,
                timeframe=timeframe,
                epochs=con.EPOCHS,
                batch_size=con.BATCH_SIZE,
            )
            self.storage_service.save(module, model)
            metrics = self.metric_service.evaluate(
                model=model,
                df_candle=df_candle,
                df_engineering=df_engineering,
                module=module,
            )
            metrics_by_timeframe[timeframe] = metrics
            self.meta_service.update_learning_history(
                module=module,
                metrics_by_timeframe=metrics_by_timeframe,
            )
        return {
            "module_id": module.module_id,
            "metrics": metrics_by_timeframe,
        }
