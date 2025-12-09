import json
import os
from copy import deepcopy
from pathlib import Path
from app.config import config as con
from features.learning.service.sql_service import SQLService
from features.learning.usecase.train import TrainUseCase
from features.learning.domain.entities.config import Config
class FetchAndSaveUseCase:
    def __init__(self):
        self.sql = SQLService()
    def execute(self, timeframe="1M"):
        train_uc = TrainUseCase()     
        # --- SỬA LỖI: Thêm đoạn code Load Config từ file bên ngoài ---
        user_config = self._load_user_config()     
        modules = []
        for _ in range(con.NUMBER_MODULE_EACH_RUN):
            # Truyền user_config vào hàm execute để TrainUseCase dùng nó
            module_entity = train_uc.execute(timeframe=timeframe, config=user_config)
            module_entity = self._normalize_entity(module_entity)
            modules.append(module_entity)
        self.sql.save(modules)
    def _load_user_config(self):
        try:
            path = Path("config.json")
            if not path.exists():
                path = Path(__file__).resolve().parents[3] / "config.json"
            if path.exists():
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    print(f"✅ Đã đọc được file config của bạn: {data.get('note')}")
                    return Config(
                        seed=data.get("seed"),
                        window_size=data.get("window_size", 30),
                        num_classes=data.get("num_classes", 6),
                        feature_cols=data.get("feature_cols", []),
                        note=data.get("note", "")
                    )
        except Exception as e:
            print(f"⚠️ Lỗi đọc config: {e}")
        return None

    def _normalize_entity(self, module_entity):
        e = deepcopy(module_entity)
        if isinstance(e.feature_cols, list):
            e.feature_cols = json.dumps(e.feature_cols, ensure_ascii=False)
        if e.note is None:
            e.note = ""
        return e