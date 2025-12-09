from copy import deepcopy
import json
from app.config import config as con
from features.learning.service.sql_service import SQLService
from features.learning.usecase.train import TrainUseCase
class FetchAndSaveUseCase:
    def __init__(self):
        self.sql = SQLService()

    def execute(self, timeframe="1M"):
        train_uc = TrainUseCase()
        modules = []
        for _ in range(con.NUMBER_MODULE_EACH_RUN):
            module_entity= train_uc.execute(timeframe=timeframe)
            module_entity = self._normalize_entity(module_entity)
            modules.append(module_entity)
        self.sql.save(modules)

    def _normalize_entity(self, module_entity):
        e = deepcopy(module_entity)
        if isinstance(e.feature_cols, list):
            e.feature_cols = json.dumps(e.feature_cols, ensure_ascii=False)
        if e.note is None:
            e.note = ""
        return e

